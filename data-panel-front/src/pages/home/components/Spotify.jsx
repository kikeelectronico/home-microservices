import React, { useState, useEffect } from "react";
import "./spotify.css"

export default function Spotify(props) {

    const [time, setTime] = useState(0)

    useEffect(() => {
        setTime(props.spotify.playing.time)
    }, [props.spotify])

    useEffect(() => {
        const intervalId = setInterval(() => {
            setTime(prevTime => prevTime + 1)
        }, 1000)

        return () => {
            clearInterval(intervalId)
        }
    }, [])

    return (
        <div className={"spotifyCard" + (props.spotify.playing.playing ? " homeCardAlphaChannel" : "")}>
            <div
                className="spotifyImageCard"
                style={{ 
                    backgroundImage:  "url(" + props.spotify.playing.image + ")"
                }}
            >
            </div>
            <div className="spotifyData">
                <div className="spotifyTitle">
                    {props.spotify.playing.track_name.length > 60 ? props.spotify.playing.track_name.substring(0, 60) + "..." : props.spotify.playing.track_name}
                </div>
                <div className="spotifyArtist">
                    {props.spotify.playing.artists.length > 40 ? props.spotify.playing.artists.substring(0, 40) + "..." : props.spotify.playing.artists}
                </div>
                <div className="spotifyDevice">
                    {props.spotify.playing.device} ({props.spotify.playing.volume})
                </div>
                <div className="spotifyBarContainer">
                    <div className="spotifyProgressBar">
                        <div
                            className="spotifyProgressBarCompleted"
                            style={{width: ((time/props.spotify.playing.duration)*100).toString() + "%"}}
                        >
                        
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}