# compiler

* <Программа> ::= <Объявление переменных> <Описание вычислений>.
* <Описание вычислений> ::= Begin <Список присваиваний> End
* <Объявление переменных> ::= Var  <Список переменных> :Boolean;
* <Список переменных> ::= <Идент> | <Идент> , <Список переменных>
* <Список присваиваний>::= <Присваивание> | <Присваивание> <Список присваиваний>
* <Присваивание> ::= <Идент> = <Выражение> ;
* <Выражение> ::= <Ун.оп.> <Подвыражение> | <Подвыражение>
* <Подвыражение> :: = ( <Выражение> ) | <Операнд> | < Подвыражение > <Бин.оп.> <Подвыражение>
* <Ун.оп.> ::= ".NOT."
* <Бин.оп.> ::= ".AND." | ".OR." | ".XOR."
* <Операнд> ::= <Идент> | <Константа>
* <Идент> ::= <Буква> <Идент> | <Буква>
* <Константа> ::= 0 | 1