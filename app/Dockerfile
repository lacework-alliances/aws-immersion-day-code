FROM public.ecr.aws/bitnami/node:16.6.0

WORKDIR /usr/src/app

COPY . .

RUN npm install

RUN npm run build --prod

FROM public.ecr.aws/nginx/nginx:1.21-alpine

RUN apk update
RUN apk add openssl

RUN mkdir -p /etc/nginx/ssl/
COPY nginx.conf /etc/nginx/nginx.conf
RUN openssl req -new -newkey rsa:2048 -days 365 -sha256 -nodes -x509 -subj "/C=US/ST=WA/L=Seattle/O=Lacework/CN=dev.lacework.net" -addext "subjectAltName = DNS:dev.lacework.net" -addext "extendedKeyUsage = serverAuth" -keyout /etc/nginx/ssl/nginx.key  -out /etc/nginx/ssl/nginx.cert

COPY --from=0 /usr/src/app /usr/src/app
COPY --from=0 /usr/src/app/dist/demo-app/ /usr/share/nginx/html
