import React from 'react'

export default function ({testContent}) {
    return (
        <div>
            <span className="font-semibold">Задание:</span> {testContent.question}
        </div>
    )
}
