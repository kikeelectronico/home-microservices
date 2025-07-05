import React, { useState, useEffect } from "react";

import Outdoors from "./components/Outdoors"
import Livingroom from "./components/rooms/Livingroom";
import Bathroom from "./components/rooms/Bathroom";
import Bedroom from "./components/rooms/Bedroom";
import Power from "./components/Power";
import NotAtHome from "../../components/NotAtHome"
import Connection from "./components/Connection";
import Spotify from "./components/Spotify";

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
  const [spotify, setSpotify] = useState(null)
  const [spotify_playing, setSpotifyPlaying] = useState(false);
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
            { weather && weather_flag.current ? <Outdoors weather={weather} water={water} playing={spotify_playing}/> : <></> }
            { home && home_flag ? <Power home={home} playing={spotify_playing}/> : <></> }
            { internet ? <Connection internet={internet} see_closed={see_closed} playing={spotify_playing}/> : <></> }
            { spotify && spotify.playing.playing ? <Spotify spotify={spotify}/> : <></> } 
          </div>
          <div className="homeCardsColumn">
            { home && home_flag ?
              <>
                <Livingroom home={home} playing={spotify_playing}/>
                <Bathroom home={home} playing={spotify_playing}/>
                <Bedroom home={home} playing={spotify_playing}/>
              </> 
            : <></> }

          </div>

          { home && home_flag ? <NotAtHome data={home}/> : <></> }

          {/* 
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
           */}
        </div>
    </div>
  )
}