import React, { useState } from 'react'

export default function PracticeContent({ practiceContent }) {
  const [isSolution, setIsSolution] = useState<boolean>(false)
  console.log(practiceContent)
  return (
    <div>
      <h6>{practiceContent.task}</h6>
      <div className='mt-[10px]'>
       <textarea className="textarea w-full" placeholder="Ваше решение"></textarea>
       <div className="flex justify-center mt-[10px]">
       <button className="btn btn-primary">Проверить</button>
       </div>
        
      </div>
    </div>
  )
}
