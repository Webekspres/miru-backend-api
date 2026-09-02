#!/usr/bin/env bash
# Shared helpers for backup.sh / restore.sh / backup_weekly.sh / test_restore.sh.
# Sourced, not executed. Resolves pg_dump/pg_restore via host clients or the
# Postgres container publishing DB_PORT (docker or podman).

_BACKUP_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIRU_ROOT="$(cd "${_BACKUP_LIB_DIR}/.." && pwd)"

miru_load_env() {
    local env_file="${1:-${MIRU_ROOT}/.env}"
    local line key val
    [ -f "$env_file" ] || return 0
    while IFS= read -r line || [ -n "$line" ]; do
        line="${line#"${line%%[![:space:]]*}"}"
        [ -z "$line" ] && continue
        case "$line" in
            \#*) continue ;;
        esac
        case "$line" in
            export\ *) line="${line#export }" ;;
        esac
        key="${line%%=*}"
        val="${line#*=}"
        case "$key" in
            ''|*[!A-Za-z0-9_]*) continue ;;
        esac
        # Do not override vars already in the environment (DB_NAME=isolasi, BACKUP_DIR=...).
        if [ -n "${!key+x}" ]; then
            continue
        fi
        val="${val%\"}"
        val="${val#\"}"
        val="${val%\'}"
        val="${val#\'}"
        export "${key}=${val}"
    done < <(tr -d '\r' < "$env_file")
}

miru_container_runtime() {
    if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
        echo docker
        return
    fi
    if command -v podman >/dev/null 2>&1; then
        echo podman
        return
    fi
    echo none
}

miru_find_db_container() {
    if [ -n "${PG_CONTAINER:-}" ]; then
        echo "$PG_CONTAINER"
        return
    fi
    local runtime port
    runtime="$(miru_container_runtime)"
    port="${DB_PORT:-5432}"
    if [ "$runtime" = none ]; then
        return
    fi
    "$runtime" ps --format '{{.Names}} {{.Ports}}' \
        | awk -v p=":${port}->" '$0 ~ p { print $1; exit }'
}

miru_pg_mode() {
    if command -v pg_dump >/dev/null 2>&1 \
        && command -v pg_restore >/dev/null 2>&1 \
        && command -v psql >/dev/null 2>&1; then
        echo host
        return
    fi
    if [ -n "$(miru_find_db_container)" ]; then
        echo container
        return
    fi
    echo missing
}

miru_require_pg() {
    local mode
    mode="$(miru_pg_mode)"
    if [ "$mode" = missing ]; then
        echo "ERROR: pg_dump/pg_restore/psql tidak ada di PATH, dan container Postgres yang publish port ${DB_PORT:-5432} tidak ditemukan." >&2
        echo "Install postgresql-client, atau set PG_CONTAINER ke nama container db." >&2
        return 1
    fi
}

miru_pg_dump() {
    local mode container runtime
    mode="$(miru_pg_mode)"
    if [ "$mode" = host ]; then
        pg_dump \
            --host="${DB_HOST}" \
            --port="${DB_PORT}" \
            --username="${DB_USER}" \
            --dbname="${DB_NAME}" \
            --format=custom \
            "$@"
    elif [ "$mode" = container ]; then
        container="$(miru_find_db_container)"
        runtime="$(miru_container_runtime)"
        "$runtime" exec -e "PGPASSWORD=${DB_PASSWORD:-}" -i "$container" \
            pg_dump -U "$DB_USER" -d "$DB_NAME" --format=custom "$@"
    else
        miru_require_pg
        return 1
    fi
}

miru_pg_restore() {
    local mode container runtime
    mode="$(miru_pg_mode)"
    if [ "$mode" = host ]; then
        pg_restore \
            --host="${DB_HOST}" \
            --port="${DB_PORT}" \
            --username="${DB_USER}" \
            --dbname="${DB_NAME}" \
            --clean \
            --if-exists \
            "$@"
    elif [ "$mode" = container ]; then
        container="$(miru_find_db_container)"
        runtime="$(miru_container_runtime)"
        "$runtime" exec -e "PGPASSWORD=${DB_PASSWORD:-}" -i "$container" \
            pg_restore -U "$DB_USER" -d "$DB_NAME" --clean --if-exists "$@"
    else
        miru_require_pg
        return 1
    fi
}

miru_psql() {
    local dbname="${1:-${DB_NAME}}"
    shift || true
    local mode container runtime
    mode="$(miru_pg_mode)"
    if [ "$mode" = host ]; then
        psql \
            --host="${DB_HOST}" \
            --port="${DB_PORT}" \
            --username="${DB_USER}" \
            --dbname="$dbname" \
            "$@"
    elif [ "$mode" = container ]; then
        container="$(miru_find_db_container)"
        runtime="$(miru_container_runtime)"
        "$runtime" exec -e "PGPASSWORD=${DB_PASSWORD:-}" -i "$container" \
            psql -U "$DB_USER" -d "$dbname" "$@"
    else
        miru_require_pg
        return 1
    fi
}

miru_valid_ident() {
    case "$1" in
        ''|*[!a-zA-Z0-9_]*)
            echo "ERROR: nama database tidak valid: $1" >&2
            return 1
            ;;
    esac
}

miru_ensure_database() {
    local target="$1"
    miru_valid_ident "$target"
    miru_valid_ident "${DB_USER}"
    miru_psql postgres -v ON_ERROR_STOP=1 -c \
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${target}' AND pid <> pg_backend_pid();" \
        >/dev/null
    miru_psql postgres -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS \"${target}\";" >/dev/null
    miru_psql postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"${target}\" OWNER \"${DB_USER}\";" >/dev/null
}

miru_drop_database() {
    local target="$1"
    miru_valid_ident "$target"
    miru_psql postgres -v ON_ERROR_STOP=1 -c \
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${target}' AND pid <> pg_backend_pid();" \
        >/dev/null
    miru_psql postgres -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS \"${target}\";" >/dev/null
}

miru_gpg_encrypt() {
    gpg --symmetric \
        --cipher-algo AES256 \
        --batch \
        --yes \
        --pinentry-mode loopback \
        --passphrase "$GPG_PASSPHRASE" \
        --output "$1"
}

miru_gpg_decrypt() {
    gpg --decrypt \
        --batch \
        --yes \
        --pinentry-mode loopback \
        --passphrase "$GPG_PASSPHRASE" \
        "$1"
}
