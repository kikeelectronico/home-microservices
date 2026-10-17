import React from "react";
import ProgressBar from 'react-bootstrap/ProgressBar';
import 'bootstrap/dist/css/bootstrap.min.css';
import "./spotify.css"

export default function Spotify(props) {

  return (
    <>
      {
        props.data && props.data.playing.playing ? 
          <div className="spotifyCard">
            <div className="spotifyData">
              <div className="spotifyTitle">
                {props.data.playing.track_name.length > 60 ? props.data.playing.track_name.substring(0, 60) + "..." : props.data.playing.track_name}
              </div>
              <hr className="spotifyArtistsSeparator"/>
              <div className="spotifyArtist">
                {props.data.playing.artists.length > 40 ? props.data.playing.artists.substring(0, 40) + "..." : props.data.playing.artists}
              </div>
              <hr className="spotifyArtistsSeparator"/>
              <div className="spotifyDevice">
                {props.data.playing.device} ({props.data.playing.volume})
              </div>
            </div>

            <div
              className="spotifyImageCard"
              style={{ 
                backgroundImage:  "url(" + props.data.playing.image + ")"
              }}
            >
            </div>

            <div className="spotifyProgressBar">
              <ProgressBar animated variant="info" now={props.data.playing.time} max={props.data.playing.duration} />
            </div>
          </div>
        : <></>
      }
    </> 
  )
}