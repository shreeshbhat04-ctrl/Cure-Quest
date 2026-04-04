from pprint import pprint

from cure_quest.adapters.analytics import BigQueryAnalyticsAdapter


def main() -> None:
    adapter = BigQueryAnalyticsAdapter()
    result = adapter.ensure_table()
    pprint(result)


if __name__ == "__main__":
    main()
