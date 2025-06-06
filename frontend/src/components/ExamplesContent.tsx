import React from 'react'

export default function ExamplesContent({examplesContent}) {
  console.log(examplesContent)
  return (
    <div className='overflow-auto'>
      {examplesContent.examples.map((code) => (
        <pre>
        <code>{code}</code>
        </pre>
      ))}
      
    </div>
  )
}
