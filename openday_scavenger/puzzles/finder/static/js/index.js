// ************************* START of Cick based Method *******************************

function getCachedSession(key)
{
  const formPuzzleName = document.getElementById("name");
  const puzzleName = formPuzzleName.defaultValue;
  const newKey=`${puzzleName}_${key}`;
  return JSON.parse(sessionStorage.getItem(newKey));
}

function saveSession(key, value)
{
  const formPuzzleName = document.getElementById("name");
  const puzzleName = formPuzzleName.defaultValue;

  const newKey=`${puzzleName}_${key}`;
  return  sessionStorage.setItem(newKey,JSON.stringify(value)) ;
}


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
   const btnHint = document.getElementById("btn-hint");
   const hide = btnHint.getAttribute('data-hide') ;
   if(hide==="0")
   {
      btnHint.setAttribute('data-hide',"1");
      hintWords.style.visibility="hidden";
      btnHint.innerText="🤯 I need a hint!";
   }
   else
   {
      btnHint.setAttribute('data-hide',"0");
      hintWords.style.visibility="visible";
      btnHint.innerText="Hide hints 😃";
   }
}


function addFoundWords(new_word)
{
    // add the new_word into the found words list 
    const found_words = document.getElementById("words");
    const innerDiv = document.createElement('div');
    innerDiv.setAttribute("id",`${new_word}-parent`);
    innerDiv.classList.add("word");
    innerDiv.classList.add("btn");
    innerDiv.classList.add("btn-outline-secondary");
    // innerDiv.classList.add("rounded-pill");
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
        var words = getCachedSession("words") ;//JSON.parse(sessionStorage.getItem("words"));
        const filtered_words = words.filter((item)=>{
            if(item['word']===word)
            {
                const char_list = item["char_list"];
                updateCellBasedOnCharList(false, char_list,null);
                updateCellBasedOnWords(char_list,false);
            }
            return item['word']!==word;
        });
        filtered_words.forEach((item)=>{
            const word_char = item['char_list'];
            updateCellBasedOnWords(word_char,true);
        });
        saveSession("words",filtered_words);//sessionStorage.setItem("words",JSON.stringify(filterd_words));
        document.getElementById(`${word}-parent`).remove();

      });

}

function extractChar(total, value, index, array) {
  return total + value["char"];
}

const submitForm = async () => {
  const name = document.getElementById("name");
  const visitor = document.getElementById("visitor");
  const words = getCachedSession("words") ;// JSON.parse(sessionStorage.getItem("words"));
  const answer = words.map(item=> item['word'].toLowerCase());
  answer.sort();
  // Construct a FormData instance
  const formData = new FormData();
  const path = window.location.pathname;
  // Add a text field
  formData.append("name", name.defaultValue);
  formData.append("visitor", visitor.defaultValue);
  formData.append("answer", answer.join()); // join with comma

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
    var char_list = getCachedSession("char_list") ;//JSON.parse(sessionStorage.getItem("char_list"));
    if (!char_list || char_list.length===0)
    {
      return;
    }
    // update char_list chars data-is-in-word to 1
    updateCellBasedOnCharList(true,char_list,null);
    updateCellBasedOnWords(char_list,true);

    // update words
    var new_word= char_list.reduce(extractChar,"");
    var words = getCachedSession("words") ;//JSON.parse(sessionStorage.getItem("words"));
    addFoundWords(new_word);
    if (!words)
    {
      words = Array();
    }
    words.push({"word":new_word,"char_list":char_list});
    saveSession("words",words);//sessionStorage.setItem("words",JSON.stringify(words));

    // after adding the char_list into words, should empty the char_list
    saveSession("char_list",[]);//sessionStorage.setItem("char_list",JSON.stringify([]));
  }
}

 function onClickCell()
{ 
    var currDirection =getCachedSession("currDirection") ; // JSON.parse(sessionStorage.getItem("currDirection"));
    const char = this.getAttribute("data-text");
    const row = this.getAttribute("data-row");
    const col = this.getAttribute("data-col");
    const selected = this.getAttribute("data-selected");

    var char_list = getCachedSession("char_list") ; //JSON.parse(sessionStorage.getItem("char_list"));

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
    
    saveSession("char_list",char_list);//sessionStorage.setItem("char_list", JSON.stringify(char_list));
    saveSession("currDirection",currDirection);//sessionStorage.setItem("currDirection", JSON.stringify(currDirection));
}


 function initFromSessionStorage(){
  var char_list = getCachedSession("char_list") ;//JSON.parse(sessionStorage.getItem("char_list"));
  var words = getCachedSession("words") ;// JSON.parse(sessionStorage.getItem("words"));

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
}
// ************************* END of Cick based Method *******************************


// ************************ START of mouse drag/touch based Method *****************************
var startMove = false;


class posData {
  constructor(event) {
    this._e = event;
    switch (event.type) {
      case "mousedown":
      case "mouseup":
      case "mousemove":
        this._x = this._e.clientX;
        this._y = this._e.clientY;
        break;
      case "touchstart":
      case "touchend":
      case "touchmove":
        this._x = this._e.originalEvent.touches[0].pageX;
        this._y = this._e.originalEvent.touches[0].pageY;
        break;
    }
  }
  get x() {return this._x;}
  get y() {return this._y;}
}


class cellData {
  constructor(cell) {
    this._cell = cell;
  }
  get cell() {return this._cell;}
  get row() {return this.cell.getAttribute("data-row");}
  get col() {return this.cell.getAttribute("data-col");}
  get char() {return this.cell.getAttribute("data-text");}
  get selected() {return this.cell.getAttribute("data-selected");}
}


function onStartDown(e){
  // console.log("onstartdown", e, e.type);
  const pos = new posData(e);
  var xPos = pos.x // e.clientX; //e.originalEvent.touches[0].pageX;
  var yPos = pos.y // e.clientY; //e.originalEvent.touches[0].pageY;
  const cell = document.elementFromPoint(xPos, yPos);
  const cd = new cellData(cell);
  var char_list = getCachedSession("char_list") ;//JSON.parse(sessionStorage.getItem("char_list"));

  if(char_list)
  { 
    updateCellBasedOnCharList(false,char_list,[cd.row,cd.col]);
  }
  
  cell.classList.add("item-selected");
  cell.setAttribute("data-selected",1);
  const is_in_word=cell.getAttribute("data-is-in-word");

  if (is_in_word==="1")
  {
    cell.classList.remove("item-is-in-word");
  }

  char_list=[{"char":cd.char,"row":cd.row,"col":cd.col}];
  saveSession("char_list",char_list); // sessionStorage.setItem("char_list", JSON.stringify(char_list));
  saveSession("currDirection",null); // sessionStorage.setItem("currDirection", null);

  startMove = true;
}


function selectCell(cell,char,row,col,char_list)
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


function onMove(e){
  const pos = new posData(e);
  var xPos = pos.x // e.clientX; //e.originalEvent.touches[0].pageX;
  var yPos = pos.y // e.clientY; //e.originalEvent.touches[0].pageY;

  var currDirection = getCachedSession("currDirection") ; //JSON.parse(sessionStorage.getItem("currDirection"));
  var char_list = getCachedSession("char_list") ;//JSON.parse(sessionStorage.getItem("char_list"));

  // cell data
  const cell = document.elementFromPoint(xPos, yPos);
  const cd = new cellData(cell);

  // if(!currDirection)
  // {
  // }

  if(!startMove)
  {
    return;
  }

  if(char_list  && char_list.length!==0)
  {
    const last_item = char_list.at(-1);
    console.log("last_item",last_item,cd.row,cd.col);
    if (last_item["row"]===cd.row && last_item["col"]===cd.col)
    {
      console.log("same cell, ignore");
      return;
    }
    else if (!currDirection)
    {
      console.log("Get the currDirection based on the second item");
      currDirection=[cd.row-last_item["row"],cd.col-last_item["col"]];
      saveSession("currDirection",currDirection); // sessionStorage.setItem("currDirection", JSON.stringify(currDirection));
      selectCell(cell,cd.char,cd.row,cd.col,char_list);
    }
    else
    {
      // based on the currDirection to get the new cell that need to be added
      // get the cell, row, col, char,
      if(currDirection[0]!==(cd.row-last_item["row"]) || currDirection[1]!==(cd.col-last_item[1]))
        {
          console.log("wrong direction, try fixing it");
          const new_id_x = parseInt(last_item["row"])+currDirection[0];
          const new_id_y = parseInt(last_item["col"])+currDirection[1];
          if (new_id_x<=parseInt(cd.row) && new_id_y<=parseInt(cd.col))
          {
            const new_cell = document.getElementById(`${parseInt(last_item["row"])+currDirection[0]}-${parseInt(last_item["col"])+currDirection[1]}`);
            const new_cd = new cellData(new_cell);
            selectCell(new_cell,new_cd.char,new_cd.row,new_cd.col,char_list);
          }
        }
    }
  }
  saveSession("char_list",char_list); //sessionStorage.setItem("char_list", JSON.stringify(char_list));
}

function onEndUp(e){
  // console.log("onendup", e, e.type);
  startMove = false;

  const pos = new posData(e);
  var xPos = pos.x // e.clientX;
  var yPos = pos.y // e.clientY;

  const cell = document.elementFromPoint(xPos, yPos);
  const cd = new cellData(cell);
  const selected = this.getAttribute("data-selected");

  // change the char_list to be the ones meet the requirement
  var char_list = getCachedSession("char_list") ;//JSON.parse(sessionStorage.getItem("char_list"));
  // console.log("char_list",char_list);
  if (char_list.length===1)
  {
    const start = char_list.at(0);
    if (start["col"]===cd.col && start["row"]===cd.row)
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
// ************************ END of mouse/touch based Method   *****************************


// ************************* START of Main *******************************
document.addEventListener("DOMContentLoaded", async function () {

    initFromSessionStorage();

    // const chars = document.querySelectorAll(".cell");
    // chars.forEach((char) => {
    //   char.addEventListener("click", onClickCell);
    // });

    const puzzle = document.getElementById("puzzle");

    puzzle.addEventListener("mousedown", onStartDown); //touchstart
    puzzle.addEventListener("mousemove", onMove); //touchmove
    puzzle.addEventListener("mouseup", onEndUp); //touchend

    puzzle.addEventListener("touchstart", onStartDown); //touchstart
    puzzle.addEventListener("touchmove", onMove); //touchmove
    puzzle.addEventListener("touchend", onEndUp); //touchend

    const btnAdd = document.getElementById("btn-add");
    btnAdd.addEventListener("click", onClickAddWord);

    const btnSubmit = document.getElementById("btn-submit");
    btnSubmit.addEventListener("click", submitForm); 

    const btnHint = document.getElementById("btn-hint");
    btnHint.addEventListener("click", displayHideHint ); 
  });