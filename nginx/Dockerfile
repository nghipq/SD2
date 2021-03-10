#use nginx image
FROM nginx

#remove the default nginx config
RUN rm /etc/nginx/conf.d/default.conf

#replace with our own nginx.conf
COPY nginx.conf /etc/nginx/conf.d/