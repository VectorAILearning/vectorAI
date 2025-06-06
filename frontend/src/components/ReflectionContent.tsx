import React from 'react'

export default function ReflectionContent({reflectionContent}) {
    return (
        <div>
            <span className="font-semibold">Рефлексия:</span> {reflectionContent.prompt}
        </div>
    )
}
