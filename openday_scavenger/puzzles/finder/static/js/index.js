// ************************* START of Cick based Method *******************************
function updateCellBasedOnCharList(select , char_list, ignoreIdx )
{
    char_list.forEach((item)=>{
        const cell =document.getElementById(item['row']+"-"+item['col']);
        const is_in_word=cell.getAttribute("data-is-in-word");
        if (!ignoreIdx)
        {
            // ignoreIdx is for ignoring in select or deselect
            ignoreIdx=[-1,-1];
        }
        if(item['row']!==ignoreIdx[0] || item['col']!==ignoreIdx[1])
        {
            if (select)
            {
                cell.classList.add("item-selected");
                if (is_in_word==="1")
                {
                  cell.classList.remove("item-is-in-word");
                }
                cell.setAttribute("data-selected",1);
            }
            else
            {  
                cell.classList.remove("item-selected");
                cell.setAttribute("data-selected",0);
                if (is_in_word==="1")
                {
                  cell.classList.add("item-is-in-word");
                }
            }
        }
    })
}

function updateCellBasedOnWords(char_list,inWord)
{
    char_list.forEach((item)=>{
      const cell =document.getElementById(item['row']+"-"+item['col']);

      if(inWord)
      {
          cell.setAttribute("data-is-in-word",1);
          cell.classList.add("item-is-in-word");
          cell.setAttribute("data-selected",0);
      }
      else
      {
          cell.setAttribute("data-is-in-word",0);
          cell.classList.remove("item-is-in-word");

      }

  })
}

function displayHideHint( ){
   const hintWords = document.getElementById("hint-words");
   const btnHint =document.getElementById("btn-hint");
   const hide = btnHint.getAttribute('data-hide') ;
   if(hide==="0")
   {
      btnHint.setAttribute('data-hide',"1");
      hintWords.style.visibility="hidden";
      btnHint.innerText="🤯 Show me the words";
   }
   else
   {
      btnHint.setAttribute('data-hide',"0");
      hintWords.style.visibility="visible";
      btnHint.innerText="😃 Hide the words";
   }
}


function addFoundWords(new_word)
{
    // add the new_word into the found words list 
    const found_words=document.getElementById("words");
    const innerDiv = document.createElement('div');
    innerDiv.setAttribute("id",`${new_word}-parent`);
    innerDiv.classList.add("word");
    const innerText = document.createElement('div');
    innerText.classList.add("word-text");
    innerText.textContent=new_word;

    const innerBtn = document.createElement("i");
    innerBtn.classList.add("fa-sharp");
    innerBtn.classList.add("fa-solid");
    innerBtn.classList.add("fa-xmark");
    // innerBtn.appendChild(icon);
    innerBtn.setAttribute("data-word",new_word);
    innerDiv.appendChild(innerText);
    innerDiv.appendChild(innerBtn);
    found_words.appendChild(innerDiv);

    
    innerBtn.addEventListener("click", function () {
        // remove this word and remove the highlight for the related chars
        const word = this.getAttribute("data-word");
        var words = JSON.parse(sessionStorage.getItem("words"));
        console.log("delete this word",word);
        const filterd_words = words.filter((item)=>{
            if(item['word']===word)
            {
                const char_list = item["char_list"];
                updateCellBasedOnCharList(false, char_list,null);
                updateCellBasedOnWords(char_list,false);
            }
            return item['word']!==word;
        });
        console.log("filtered_words",filterd_words);
        filterd_words.forEach((item)=>{
            const word_char = item['char_list'];
            updateCellBasedOnWords(word_char,true);
        });
        sessionStorage.setItem("words",JSON.stringify(filterd_words));
        document.getElementById(`${word}-parent`).remove();

      });

}

function extractChar(total, value, index, array) {
  return total + value["char"];
}

 const submitForm = async () => {
  const name = document.getElementById("name");
  const visitor = document.getElementById("visitor");
  const words = JSON.parse(sessionStorage.getItem("words"));
  const answer = words.map(item=> item['word']);
  answer.sort();
  // Construct a FormData instance
  const formData = new FormData();
  const path = window.location.pathname;
  // Add a text field
  formData.append("name", name.defaultValue);
  formData.append("visitor", visitor.defaultValue);
  formData.append("answer", answer.join()); // join with comma

  // fetch(`/submission`, {
  //     method: "POST",
  //     // Set the FormData instance as the request body
  //     body: formData,
  //   }).then( (response) => {
  //     // The API call was successful!
  //     // return response.body();
  //     console.log("Received response",response);
  //   }).then((html) => {
  //     document.body.innerHTML = html;
  //   }).catch(function (err) {
  //     // There was an error
  //     console.warn('Something went wrong.', err);
  //   });

  try {
    const response = await fetch(`/submission`, {
      method: "POST",
      // Set the FormData instance as the request body
      body: formData,
    });
    const html = await response.text();
    document.body.innerHTML = html;
  } catch (e) {
    console.error(e);
  }
};


 function onClickAddWord(){
  {
    // add the word to the session state
    var char_list = JSON.parse(sessionStorage.getItem("char_list"));
    if (!char_list || char_list.length===0)
    {
      return;
    }
    // update char_list chars data-is-in-word to 1
    updateCellBasedOnCharList(true,char_list,null);
    updateCellBasedOnWords(char_list,true);

    // update words
    var new_word= char_list.reduce(extractChar,"");
    var words = JSON.parse(sessionStorage.getItem("words"));
    addFoundWords(new_word);
    if (!words)
    {
      words = Array();
    }
    words.push({"word":new_word,"char_list":char_list});
    sessionStorage.setItem("words",JSON.stringify(words));

    // after adding the char_list into words, should empty the char_list
    sessionStorage.setItem("char_list",JSON.stringify([]));
  }
}

 function onClickCell()
{ 
    var currDirection = JSON.parse(sessionStorage.getItem("currDirection"));
    console.log("Click");
    const char = this.getAttribute("data-text");
    const row = this.getAttribute("data-row");
    const col = this.getAttribute("data-col");
    const selected = this.getAttribute("data-selected");

    var char_list = JSON.parse(sessionStorage.getItem("char_list"));

    if (!char_list || char_list.length===0)
    {
        char_list=[{"char":char,"row":row,"col":col}];
        currDirection=null;
    }
    else
    {
        const last_item = char_list.at(-1);
        if (selected==="1" || 
          (Math.abs(last_item["row"]- row)>1 || Math.abs(last_item["col"]-col)>1) || 
          (currDirection && !(((row-last_item["row"]) ===currDirection[0])&&((col-last_item["col"]) ===currDirection[1])) )
        )
        {
            updateCellBasedOnCharList(false,char_list,[row,col]);
            char_list=[{"char":char,"row":row,"col":col}];
            currDirection=null;
        }
        else
        {
            
            char_list.push({"char":char,"row":row,"col":col});
            currDirection = [row-last_item["row"],col-last_item["col"]];
        }
    }

    this.classList.add("item-selected");
    this.setAttribute("data-selected",1);
    const is_in_word=this.getAttribute("data-is-in-word");
    if (is_in_word==="1")
    {
      this.classList.remove("item-is-in-word");
    }
    
    sessionStorage.setItem("char_list", JSON.stringify(char_list));
    sessionStorage.setItem("currDirection", JSON.stringify(currDirection));
}


 function initFromSessionStorage(){
  var char_list = JSON.parse(sessionStorage.getItem("char_list"));
  var words = JSON.parse(sessionStorage.getItem("words"));
  
  // answer number
  var num = JSON.parse(sessionStorage.getItem("num"));

  if(words)
  {
      words.forEach((item)=>{
          const word_char = item['char_list'];
          //updateCellBasedOnCharList(true, word_char,null);
          updateCellBasedOnWords(word_char,true);
          addFoundWords(item['word']);
      })
  }

  if(char_list)
  {
      updateCellBasedOnCharList(true, char_list, null);
  }

  if (!num)
  {
      const hint = document.getElementById("hint");
      num = hint.getAttribute("data-num");
      sessionStorage.setItem("num",JSON.stringify(num));
  }
}


// ************************* END of Cick based Method *******************************


// ************************ START of touch based Method *****************************

var touchStart = false;

function onTouchStart(e){
  console.log("ontouchstart");
  // var xPos = e.originalEvent.touches[0].pageX;
  // var yPos = e.originalEvent.touches[0].pageY;

  var xPos = e.clientX;
  var yPos = e.clientY;


  const cell = document.elementFromPoint(xPos, yPos);
  const char = cell.getAttribute("data-text");
  const row = cell.getAttribute("data-row");
  const col = cell.getAttribute("data-col");
  const selected = this.getAttribute("data-selected");


  var char_list = JSON.parse(sessionStorage.getItem("char_list"));
  if(char_list)
  { 
    updateCellBasedOnCharList(false,char_list,[row,col]);
  }
  
  cell.classList.add("item-selected");
  cell.setAttribute("data-selected",1);
  const is_in_word=cell.getAttribute("data-is-in-word");
  if (is_in_word==="1")
  {
    cell.classList.remove("item-is-in-word");
  }

  char_list=[{"char":char,"row":row,"col":col}];
  sessionStorage.setItem("char_list", JSON.stringify(char_list));
  sessionStorage.setItem("currDirection", null);
  touchStart = true;

}


function selectCell(cell, char,row,col,char_list)
{
  cell.classList.add("item-selected");
  cell.setAttribute("data-selected",1);
  const is_in_word=cell.getAttribute("data-is-in-word");
  if (is_in_word==="1")
  {
    cell.classList.remove("item-is-in-word");
  }

  char_list.push({"char":char,"row":row,"col":col});
  return char_list;
}


function onTouchMove(e){
  // var xPos = e.originalEvent.touches[0].pageX;
  // var yPos = e.originalEvent.touches[0].pageY;
  var xPos = e.clientX;
  var yPos = e.clientY;
  var currDirection = JSON.parse(sessionStorage.getItem("currDirection"));
  var char_list = JSON.parse(sessionStorage.getItem("char_list"));
  // if(!currDirection)
  // {
    
  // }
  if(!touchStart)
  {
    return;
  }
  console.log("ontouchmove");
  
  const cell = document.elementFromPoint(xPos, yPos);
  const char = cell.getAttribute("data-text");
  const row = cell.getAttribute("data-row");
  const col = cell.getAttribute("data-col");
  const selected = this.getAttribute("data-selected");

  if(char_list  && char_list.length!==0)
  {
    const last_item = char_list.at(-1);
    console.log("last_item",last_item,row,col);
    if (last_item["row"]===row && last_item["col"]===col)
    {
      console.log("same cell, ignore");
      return;
    }
    else if (!currDirection)
    {
      console.log("Get the currDirection based on the second item");
      currDirection=[row-last_item["row"],col-last_item["col"]];
      sessionStorage.setItem("currDirection", JSON.stringify(currDirection));
      selectCell(cell, char,row,col,char_list);
    }
    else
    {
      // console.log("Fix direction");
      // based on the currDirection to get the new cell that need to be added
      // get the cell, row, col, char,
      if(currDirection[0]!==(row-last_item["row"]) || currDirection[1]!==(col-last_item[1]))
        {
          console.log("wrong direction, try fixing it");
          const new_id_x = parseInt(last_item["row"])+currDirection[0];
          const new_id_y = parseInt(last_item["col"])+currDirection[1];
          if (new_id_x<=parseInt(row) && new_id_y<=parseInt(col))
          {

            const new_cell = document.getElementById(`${parseInt(last_item["row"])+currDirection[0]}-${parseInt(last_item["col"])+currDirection[1]}`);
            const new_char = new_cell.getAttribute("data-text");
            const new_row = new_cell.getAttribute("data-row");
            const new_col = new_cell.getAttribute("data-col");
            selectCell(new_cell, new_char,new_row,new_col,char_list);
          }
          
        }
      
    }
  }
  sessionStorage.setItem("char_list", JSON.stringify(char_list));

}

function onTouchEnd(e){
  touchStart=false;
  console.log("ontouchend");
  // var xPos = e.originalEvent.touches[0].pageX;
  // var yPos = e.originalEvent.touches[0].pageY;
  var xPos = e.clientX;
  var yPos = e.clientY;
  const cell = document.elementFromPoint(xPos, yPos);
  const char = cell.getAttribute("data-text");
  const row = cell.getAttribute("data-row");
  const col = cell.getAttribute("data-col");
 
  const selected = this.getAttribute("data-selected");

  // change the char_list to be the ones meet the requirement
  var char_list = JSON.parse(sessionStorage.getItem("char_list"));
  if (char_list.length===1)
  {
    const start = char_list.at(0);
    
    if (start["col"]===col && start["row"]===row)
    {
      //start cell is the same as stop cell;
      return;
    }
    else{
      console.log("add new end")
    }

  }
  else
  {
    console.log("clean up the char_list")
  }

}
// ************************ END of touch based Method   *****************************
document.addEventListener("DOMContentLoaded", async function () {

    initFromSessionStorage();
    
    const puzzle =document.getElementById("puzzle");

    puzzle.addEventListener("mousedown",onTouchStart);//touchstart
    puzzle.addEventListener("mousemove",onTouchMove); //touchmove
    puzzle.addEventListener("mouseup",onTouchEnd); //touchend

    // const chars = document.querySelectorAll(".cell");

    // chars.forEach((char) => {
    //   char.addEventListener("click", onClickCell);
    // });

    const btnAdd = document.getElementById("btn-add");
    btnAdd.addEventListener("click", onClickAddWord);

    const btnSubmit =document.getElementById("btn-submit");
    btnSubmit.addEventListener("click", submitForm); 

    const btnHint =document.getElementById("btn-hint");
    btnHint.addEventListener("click", displayHideHint ); 

  
  });