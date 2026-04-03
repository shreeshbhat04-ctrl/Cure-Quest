from pprint import pprint

from cure_quest.adapters.calendar import GoogleCalendarAdapter


def main() -> None:
    adapter = GoogleCalendarAdapter()
    event = adapter.create_demo_event("Cure-Quest demo appointment")
    print("CREATED_EVENT")
    pprint(event)


if __name__ == "__main__":
    main()
