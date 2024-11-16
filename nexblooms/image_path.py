from decouple import config

def full_image_path(path):
    switch = config("FETCH_FROM_S3",cast=bool)
    if switch:
        base_url = config("S3_STORAGE_HOST")
        return base_url + str(path)
    else:
        base_url = config("API_BASE_HOST")

        return base_url + "media/" +str(path)