# Add more subjects/questions here: (question, [options], index_of_correct_option)
QUESTIONS = {
 "Java": [
  ("Which keyword creates an object?", ["new","create","alloc","make"], 0),
  ("Java source is compiled into?", ["Machine code","Bytecode","Assembly","Script"], 1),
  ("Which is NOT a primitive type?", ["int","boolean","String","char"], 2),
  ("Keyword to inherit a class?", ["implements","extends","inherits","super"], 1),
  ("Program entry point method?", ["start()","main()","run()","init()"], 1)],
 "C": [
  ("printf format specifier for int?", ["%d","%f","%s","%c"], 0),
  ("Which operator gives the address of a variable?", ["*","&","->","#"], 1),
  ("Function for dynamic memory allocation?", ["malloc","new","alloc","create"], 0),
  ("Array index starts at?", ["1","0","-1","Depends"], 1),
  ("Header needed for printf?", ["stdlib.h","stdio.h","string.h","math.h"], 1)],
 "Python": [
  ("Which creates a list?", ["()","[]","{}","<>"], 1),
  ("Keyword to define a function?", ["func","def","function","fn"], 1),
  ("Output of len('abc')?", ["2","3","4","Error"], 1),
  ("Which type is immutable?", ["list","dict","tuple","set"], 2),
  ("Python comment starts with?", ["//","#","--","/*"], 1)],
 "SQL": [
  ("Which statement retrieves data?", ["GET","SELECT","FETCH","OPEN"], 1),
  ("Which clause filters rows?", ["WHERE","FILTER","IF","LIMIT"], 0),
  ("Which combines rows from two tables?", ["MERGE","JOIN","LINK","STACK"], 1),
  ("What uniquely identifies a row?", ["Foreign key","Index","Primary key","View"], 2),
  ("Which function counts rows?", ["SUM","COUNT","TOTAL","NUM"], 1)],
}

QUESTIONS.update({
 "JavaScript": [
  ("Which keyword declares a block-scoped variable?", ["var","let","dim","def"], 1),
  ("What does === check?", ["Value only","Type only","Value and type","Reference only"], 2),
  ("Which method adds an item to the end of an array?", ["push()","add()","append()","insert()"], 0),
  ("What does typeof null return?", ["null","undefined","object","number"], 2),
  ("Which is used to handle a Promise result?", [".then()",".next()",".done()",".run()"], 0)],
 "Web Basics": [
  ("Which tag creates a hyperlink?", ["<link>","<a>","<href>","<url>"], 1),
  ("Which CSS property changes text color?", ["font-color","text-color","color","fg"], 2),
  ("Which tag holds the page title shown in the browser tab?", ["<title>","<h1>","<meta>","<head>"], 0),
  ("Which CSS layout is one-dimensional?", ["Grid","Flexbox","Float","Table"], 1),
  ("Which attribute gives an image alternate text?", ["title","alt","src","caption"], 1)],
})
