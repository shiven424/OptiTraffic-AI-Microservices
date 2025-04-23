# gateway/Dockerfile
# ─────────────────────────────────────────────────────────────────────────────
# 1) Builder: compile the auth_jwt module
# ─────────────────────────────────────────────────────────────────────────────
FROM alpine:3.18 AS builder

# install build deps
RUN apk add --no-cache \
      build-base \
      pcre-dev \
      zlib-dev \
      openssl-dev \
      jansson-dev \
      git \
      wget

# download NGINX source matching 1.24.x
ENV NGINX_VERSION=1.24.0
RUN wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz \
 && tar zxvf nginx-${NGINX_VERSION}.tar.gz

# clone the JWT module
RUN git clone https://github.com/kjdev/nginx-auth-jwt.git /tmp/nginx-auth-jwt

WORKDIR nginx-${NGINX_VERSION}

RUN ./configure \
      --with-compat \
      --add-dynamic-module=/tmp/nginx-auth-jwt \
      --with-http_ssl_module \
      --with-http_v2_module \
 && make modules

# ─────────────────────────────────────────────────────────────────────────────
# 2) Final image: official NGINX + our module
# ─────────────────────────────────────────────────────────────────────────────
FROM nginx:1.24-alpine

# Install the jansson runtime library so our module can load
RUN apk update \
 && apk add --no-cache jansson

# Copy in the compiled JWT module
COPY --from=builder \
     /nginx-1.24.0/objs/ngx_http_auth_jwt_module.so \
     /etc/nginx/modules/

# Load modules.conf (which points to our module)
RUN printf "load_module modules/ngx_http_auth_jwt_module.so;\n" \
     > /etc/nginx/modules.conf

# Copy gateway config & key
COPY nginx.conf      /etc/nginx/nginx.conf
COPY jwt_public.pem   /etc/nginx/jwt_public.pem
COPY jwks.json       /etc/nginx/jwks.json

