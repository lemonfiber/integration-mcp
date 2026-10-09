#!/usr/bin/env bash
# Start Pebble, the authority Let's Encrypt publishes for testing, twice (once
# requiring an External Account Binding) and its challenge test server, for
# the ACME tests. Prints the settings the tests read, as `NAME=value` lines:
#
#   eval "$(scripts/pebble.sh)"          # on this machine
#   scripts/pebble.sh >> "$GITHUB_ENV"   # in CI
#
# The binding's key is made here for this run alone. Every name resolves to
# this machine, where the tests answer TLS-ALPN-01 on 5001 and HTTP-01 on 5002.
# On Linux the containers share this machine's network, so each test can give
# its name a loopback address of its own (PEBBLE_ADDRESSES=own) and tests run
# at once without answering each other's challenges; elsewhere they share one
# address (PEBBLE_ADDRESSES=shared).
# `scripts/pebble.sh stop` removes the three containers.
set -euo pipefail

PEBBLE="ghcr.io/letsencrypt/pebble@sha256:ddf230642b1a584f519f32e347de1b05a6e4c1f6c35c1863b33effeab5f78199" # 2.10.1
CHALLTESTSRV="ghcr.io/letsencrypt/pebble-challtestsrv@sha256:12ce21884def456bcf9786542113949e1f19dc7738d2c70e156c2d0c38a1405b" # 2.10.1
PYTHON="python@sha256:7bec7ddcddeff7975d6ba9b4be7dd6f6b2f55e7491539145e2978f7f97ce9144" # 3.14.6-slim-trixie
NETWORK="lemonfiber-mcp-pebble"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
HELD="${HERE}/.pebble"

stop() {
	docker rm -fv lemonfiber-mcp-pebble lemonfiber-mcp-pebble-eab lemonfiber-mcp-challtestsrv >/dev/null 2>&1 || true
	docker network rm "${NETWORK}" >/dev/null 2>&1 || true
}

if [ "${1:-}" = stop ]; then
	stop
	exit 0
fi
stop
mkdir -p "${HELD}"
chmod 0700 "${HELD}"

# Where a container reaches this machine: itself, on Linux's host network, and
# Docker Desktop's gateway elsewhere.
if [ "$(uname -s)" = Linux ]; then
	placed=(--network host)
	host_ip=127.0.0.1
	dns=127.0.0.1:8053
	addresses=own
else
	docker network create "${NETWORK}" >/dev/null
	placed=(--network "${NETWORK}")
	host_ip="$(docker run --rm "${PYTHON}" python -c 'import socket; print(socket.gethostbyname("host.docker.internal"))')"
	dns=lemonfiber-mcp-challtestsrv:8053
	addresses=shared
fi

kid="kid-1"
hmac="$(openssl rand -base64 48 | tr '+/' '-_' | tr -d '=\n')"
printf '%s' "${hmac}" > "${HELD}/eab-hmac"
chmod 0600 "${HELD}/eab-hmac"
python3 - "${HERE}/tests/pebble/pebble.json" "${HELD}" "${kid}" "${hmac}" <<'PY'
import json, pathlib, sys
plain, held, kid, hmac = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3], sys.argv[4]
config = json.loads(pathlib.Path(plain).read_text(encoding="utf-8"))
(held / "pebble.json").write_text(json.dumps(config), encoding="utf-8")
bound = config["pebble"]
bound.update(
    listenAddress="0.0.0.0:14001",
    managementListenAddress="0.0.0.0:15001",
    externalAccountBindingRequired=True,
    externalAccountMACKeys={kid: hmac},
)
(held / "pebble-eab.json").write_text(json.dumps(config), encoding="utf-8")
PY

docker run -d --name lemonfiber-mcp-challtestsrv "${placed[@]}" -p 8055:8055 "${CHALLTESTSRV}" \
	-defaultIPv4 "${host_ip}" -defaultIPv6 "" -http01 "" -https01 "" -tlsalpn01 "" >/dev/null
for name in pebble pebble-eab; do
	port=14000
	[ "${name}" = pebble-eab ] && port=14001
	docker run -d --name "lemonfiber-mcp-${name}" "${placed[@]}" -p "${port}:${port}" \
		-e PEBBLE_VA_NOSLEEP=1 -e PEBBLE_WFE_NONCEREJECT=0 \
		-v "${HELD}/${name}.json:/config.json:ro" "${PEBBLE}" -config /config.json -dnsserver "${dns}" >/dev/null
done
docker cp lemonfiber-mcp-pebble:/test/certs/pebble.minica.pem "${HELD}/roots.pem" >/dev/null

for port in 14000 14001; do
	for _ in $(seq 1 50); do
		if curl -sk "https://localhost:${port}/dir" >/dev/null; then
			break
		fi
		sleep 0.2
	done
done

echo "PEBBLE_DIRECTORY=https://localhost:14000/dir"
echo "PEBBLE_EAB_DIRECTORY=https://localhost:14001/dir"
echo "PEBBLE_ROOTS=${HELD}/roots.pem"
echo "PEBBLE_EAB_KID=${kid}"
echo "PEBBLE_EAB_HMAC_FILE=${HELD}/eab-hmac"
echo "PEBBLE_CHALLTESTSRV=http://localhost:8055"
echo "PEBBLE_ADDRESSES=${addresses}"
