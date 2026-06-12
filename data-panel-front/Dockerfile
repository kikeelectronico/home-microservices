FROM node:lts-alpine AS base
ENV REACT_APP_DATA_PANEL_API_URL="https://api.panel.home.enriquegomez.me"
RUN mkdir front
WORKDIR /front
COPY . ./
RUN npm install --no-package-lock
RUN npm run build
FROM nginx
RUN mkdir /html
COPY --from=base /front/build /html
COPY nginx_config.conf /etc/nginx/conf.d/default.conf