

export default function Pagination({currentPage, setCurrentPage, scrollToUp, maxPages}){
    return (
        <section className='pagination'>
          <button id="active-btn" onClick={() => {if(currentPage >= 2) setCurrentPage(currentPage - 1); scrollToUp();}}>{currentPage}</button>
          <button disabled={currentPage === maxPages || maxPages === 0}
                  onClick={() => {setCurrentPage(currentPage + 1); scrollToUp();}}
          >{currentPage + 1}</button>
          {currentPage < maxPages - 2 && (
            <>
              <button disabled>...</button>
              <button onClick={() => {setCurrentPage(maxPages); scrollToUp();}}>{maxPages}</button>
            </>
          )}
      </section>
    )
}