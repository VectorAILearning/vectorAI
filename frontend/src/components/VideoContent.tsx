import React from 'react'

export default function VideoContent({videoContent}) {
  return (
    <div className="flex flex-col items-center">
      <div className="font-semibold">{videoContent.title}</div>
      <div className='text-center'>{videoContent.description}</div>

      {videoContent.url && (
        <iframe width="560"
          height="315"
          src={("https://www.youtube.com/embed/" + videoContent.url.split("").splice(-11).join(""))}
          title="YouTube video player"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          referrerpolicy="strict-origin-when-cross-origin"
          allowfullscreen>
        </iframe>
      )}
      
    </div>
  )
}
