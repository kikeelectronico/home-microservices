import React, { useState, useEffect } from "react";

import Outdoors from "./components/Outdoors"
import Room from "./components/Room";

import "./home.css"

const API = process.env.REACT_APP_DATA_PANEL_API_URL

const scenes_to_show = [
  {
    "name": "Luz indirecta",
    "id": "scene_dim"
  }
]

const home_alerts = [
  {
    "text": "Humedad baja",
    "severity": "normal",
    "image": "drops.png",
    "conditions": [
      {
        "device_id": "thermostat_livingroom",
        "param": "thermostatHumidityAmbient",
        "value": 30,
        "comparator": "<"
      }
    ]
  },
  {
    "text": "Humedad alta",
    "severity": "normal",
    "image": "drops.png",
    "conditions": [
      {
        "device_id": "thermostat_livingroom",
        "param": "thermostatHumidityAmbient",
        "value": 55,
        "comparator": ">"
      }
    ]
  },
  {
    "text": "Salón",
    "severity": "normal",
    "image": "window.png",
    "conditions": [
      {
        "device_id": "e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4",
        "param": "openPercent",
        "value": 100,
        "comparator": "="
      }
    ]
  },
  {
    "text": "Dormitorio",
    "severity": "normal",
    "image": "window.png",
    "conditions": [
      {
        "device_id": "e6c2e2bd-5057-49bc-821f-a4b10e415ac6",
        "param": "openPercent",
        "value": 100,
        "comparator": "="
      }
    ]
  },
  {
    "text": "Abre la ventana",
    "severity": "low",
    "conditions": [
      {
        "device_id": "e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4",
        "param": "openPercent",
        "value": 0,
        "comparator": "="
      },
      {
        "device_id": "thermostat_livingroom",
        "param": "thermostatMode",
        "value": "cool",
        "comparator": "="
      },
      {
        "device_id": "thermostat_livingroom",
        "param": "thermostatTemperatureAmbient",
        "value": {
          "device_id": "temperature_001",
          "param": "temperatureAmbientCelsius"
        },
        "comparator": ">"
      }
    ]
  },
  {
    "text": "Cierra la ventana",
    "severity": "low",
    "conditions": [
      {
        "device_id": "e5e5dd62-a2d8-40e1-b8f6-a82db6ed84f4",
        "param": "openPercent",
        "value": 100,
        "comparator": "="
      },
      {
        "device_id": "scene_summer",
        "param": "thermostatMode",
        "value": true,
        "comparator": "="
      },
      {
        "device_id": "thermostat_livingroom",
        "param": "thermostatTemperatureAmbient",
        "value": {
          "device_id": "temperature_001",
          "param": "temperatureAmbientCelsius"
        },
        "comparator": "<"
      }
    ]
  }
]

export default function Home(props) {

  const [internet, setInternet] = useState(null)
  const [home, setHome] = useState(null)
  const [home_flag, setHomeFlag] = useState(null)
  const [water, setWater] = useState(null)
  const [weather, setWeather] = useState(null)
  const [weather_flag, setWeatherFlag] = useState(null)
  // const [launches, setLaunches] = useState(null)
  // const [launches_flag, setLaunchesFlag] = useState(null)
  const [spotify, setSpotify] = useState(null)
  const [spotify_playing, setSpotifyPlaying] = useState(false);
  const [weather_alerts, setWeatherAlerts] = useState(null)
  const [see_closed, setSeeClosed] = useState(false)

  useEffect(() => {
    const sse = new EventSource(API + "/stream", { withCredentials: false });
    sse.onmessage = e => {
      setSeeClosed(false)
      let event = JSON.parse(e.data)
      if (event.type === "internet") {setInternet(event.data)}
      else if (event.type === "home") {setHome(event.data); setHomeFlag(event.flags)}
      else if (event.type === "water") {setWater(event.data);}
      else if (event.type === "weather") {setWeather(event.data); setWeatherFlag(event.flags)}
      // else if (event.type === "launches") {setLaunches(event.data); setLaunchesFlag(event.flags)}
      else if (event.type === "spotify") {setSpotify(event.data)}
    };
    sse.onerror = () => {
      setSeeClosed(true)
      // sse.close();
    }
    return () => {
      sse.close();
    };
  }, [])

  useEffect(() => {
    if (spotify) {
      setSpotifyPlaying(spotify.playing.playing)
      props.setBackgroundImage(
        {
          url: spotify.playing.image,
          position: "0% " + spotify.playing.image_position*10 + "%"
        }
      )
    }
  }, [props.setBackgroundImage, spotify])

  useEffect(() => {
    if (weather_flag) {
      let _weather_alerts = []
      for (let i = 0; i < weather.alerts.alert.length; i++) {
        let alert = weather.alerts.alert[i]
        console.log(alert)
        let severity = "low"
        if (alert.category.includes("Extreme")) severity = "critical"
        else if (alert.event.includes("Moderate")) severity = "middle"
        else if (alert.event.includes("amarillo")) severity = "low"
        else if (alert.event.includes("naranja")) severity = "middle"
        _weather_alerts.push(
          {
            "text": alert.event + (alert.event[alert.event.length-1] !== "." ? "." : "") + (alert.desc !== "" ? " " + alert.desc : "") + (alert.desc[alert.desc.length-1] !== "." ? "." : "") + (alert.areas !== "" ? " " + alert.areas : ""),
            "severity": severity,
            "image": null
          }
        )
        setWeatherAlerts(_weather_alerts)
      }
    }
  }, [weather, weather_flag])

  const assertAlert = (conditions) => {
    for (let i = 0; i < conditions.length; i++) {
      let condition = conditions[i]
      switch(condition.comparator) {
        case "<":
          if (typeof(condition.value) === "object"){
            if (!(home.status[condition.device_id][condition.param] < home.status[condition.value.device_id][condition.value.param]))
              return false
          } else {
            if (!(home.status[condition.device_id][condition.param] < condition.value))
              return false
          }
          break
        case "=":
          if (typeof(condition.value) === "object") {
            if (!(home.status[condition.device_id][condition.param] === home.status[condition.value.device_id][condition.value.param]))
              return false
          } else {
            if (!(home.status[condition.device_id][condition.param] === condition.value))
              return false
          }
          break
        case ">":
          if (typeof(condition.value) === "object") {
            if (!(home.status[condition.device_id][condition.param] > home.status[condition.value.device_id][condition.value.param]))
              return false
          } else {
            if (!(home.status[condition.device_id][condition.param] > condition.value))
              return false
          }
          break
      }
    }
    return true
  }

  return (
    <div className="homePage">
        <div className="homeCardsContainer">
          <div className="homeCardsColumn">
            { weather && weather_flag.current ? <Outdoors weather={weather.current} weather_alerts={weather_alerts}/> : <></> }           
          </div>
          <div className="homeCardsColumn">
            { home && home_flag ? <Room home={home}/> : <></> }

          </div>
          {/* { home && home_flag ? <Thermostat data={home}/> : <></> }
          { weather && weather_flag.current ? <Weather data={weather.current}/> : <></> }
          { weather && weather_flag.current ? <Air data={weather.current}/> : <></> }
          { home && home_flag ? <Power data={home}/> : <></> }
          { home && home_flag ? <Shower data={home}/> : <></> }
          { home && home_flag ? <Bedroom data={home}/> : <></> }
          { home && home_flag ? <NotAtHome data={home}/> : <></> }
          {
            //{ launches && launches_flag ? <Launches data={launches}/> : <></> }
          }
          { spotify ? <Spotify data={spotify}/> : <></> }
          { 
            home ? 
              scenes_to_show.map((scene, index) => {
                return <LightingScene data={home} scene={scene} key={index}/>
              })
            : <></>
          }
          { 
            home ? 
              home_alerts.map((alert, index) => {
                if (assertAlert(alert.conditions))
                  return <Alerts alert={alert} key={index} wide={false}/>
              })
            : <></>
          }
          { 
            weather_alerts ? 
              weather_alerts.map((alert, index) => {
                  return <Alerts alert={alert} key={index} wide={true}/>
              })
            : <></>
          }
          {
            water ? 
              <>
                { 
                  water.water.level < 50 ?
                    <Alerts alert={{text: "Nivel de embalses: " + water.water.level + " %", severity: (water.water.level < 40 ? "normal" : "low")}}/>
                  : <></>}
              </>
              : <></>
          }
          { see_closed ? <Alerts alert={{text: "Sin conexión con la API", severity: "critical"}}/> : <></>}
          { internet ? <Internet data={internet}/> : <></> } */}
        </div>
    </div>
  )
}