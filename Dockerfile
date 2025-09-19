FROM mongo

COPY mongo-keyfile /etc/mongo-keyfile

RUN chmod 600 /etc/mongo-keyfile && chown mongodb:mongodb /etc/mongo-keyfile