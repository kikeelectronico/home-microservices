import React, { useState, useEffect } from "react";
import "./spotify.css"

export default function Spotify(props) {

    useEffect(() => {
        setProgress((props.spotify.playing.time/props.spotify.playing.duration)*100)
    }, [props])

    const [progress, setProgress] = useState(0)

    return (
        <div className="spotifyCard">
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
                        <div className="spotifyProgressBarCompleted" style={{width: progress.toString() + "%"}}>
                        
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}