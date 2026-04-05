from cure_quest.config import get_settings


def main() -> None:
    settings = get_settings()
    instance_uri = settings.alloydb_instance_uri

    if instance_uri is None:
        print("ALLOYDB metadata is incomplete.")
        print("Set ALLOYDB_PROJECT, ALLOYDB_REGION, ALLOYDB_CLUSTER, and ALLOYDB_INSTANCE in .env.")
        return

    print("Run this in a separate terminal before starting the API:")
    print(
        f"alloydb-auth-proxy --address {settings.alloydb_auth_proxy_host} "
        f"--port {settings.alloydb_auth_proxy_port} {instance_uri}"
    )
    print("")
    print("Then the app will connect through:")
    print(
        f"postgresql+psycopg://{settings.alloydb_user or 'USER'}:***@"
        f"{settings.alloydb_auth_proxy_host}:{settings.alloydb_auth_proxy_port}/"
        f"{settings.alloydb_database}"
    )


if __name__ == "__main__":
    main()
