import React from 'react'

export default function QuestionContent({questionContent}) {
    return (
        <div>
            <div className="font-semibold">{questionContent.question}</div>
            <ul className="list-disc ml-6">
                {questionContent.options?.map((opt: string, i: number) => (
                    <li key={i}>{opt}</li>
                ))}
            </ul>
            <div className="text-xs text-base-content/60 mt-1">
                <span className="font-semibold">Ответ:</span> {questionContent.answer}
            </div>
        </div>
    )
}
