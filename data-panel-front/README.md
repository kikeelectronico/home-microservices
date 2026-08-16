# Data panel front

It is the front end of the web panels that show information in different screens at home.

## Development

```bash
npm install
npm run dev
```

## Build

```bash
docker build --tag data-panel-front .
```

## Run

```bash
docker run -p 8001:80 -t data-panel-front
```
