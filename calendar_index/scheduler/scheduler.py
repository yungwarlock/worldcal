from storage import SpiderIndexStorage, MunchingJobStorage


def schedule_munching_job():
    spider_storage = SpiderIndexStorage.from_environment_variables()
    muching_job_storage = MunchingJobStorage.from_environment_variables()

    items = spider_storage.get_unscheduled_items()
    muching_job_storage.schedule_job(items)

    spider_storage.mark_as_scheduled(items)
