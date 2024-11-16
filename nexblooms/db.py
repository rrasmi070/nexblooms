from decouple import config, Csv


DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE'),
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', cast=int),
        'OPTIONS': {
            'autocommit': True,
            'charset': 'utf8mb4'      #// add this line for emozi
        },
    }
}

# OPTIONS =  {'charset': 'utf8mb4'}, #// add this line imog update
