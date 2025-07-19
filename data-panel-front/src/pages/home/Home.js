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
        </div>
    </div>
  )
}