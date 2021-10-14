\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}

\title{Implementar HIDS}

\author{Andrea Carosi\\
        Marcel Espejo Cuenca}
\date{Octubre 2021}

\begin{document}
\maketitle
\includegraphics[width=\textwidth]{main.PNG}
\clearpage
\tableofcontents
\clearpage
\section{Introducción}
A continuación, se presenta un resumen del desarrollo llevado a cabo para implementar un HIDS desde cero.La primera decisión importante del proyecto ha sido decantarnos por una de las dos opciones que se nos proponen en el enunciado: \begin{itemize}
    \item HIDS ya creado:Una opción es utilizar una herramienta ya implementada y enfocar el proyecto a aprender a configurar un HIDS.-Crear nuestro propio HIDS
    
    \item Crear nuestro propio HIDS: crear desde cero por lo que el proyecto consistirá en implementar toda la funcionalidad posible de un HIDS.
\end{itemize}
Finalmente hemos optado por crear nuestro propio HIDS por los siguientes motivos:Aunque utilizar un HIDS ya existente puede ser muy útil por motivos prácticos, hemos decidido enfocarnos mas en la opción que nos permite manejar cómo funciona por dentro el sistema y así comprenderlo lo mejor posible mas allá de como configurar algo que ya se ha hecho por otra persona o una empresa.

\section{Planteamiento inicial}
Seguir la estructura planteada en clase siguiendo los pasos que subdividen nuestro problema en tareas menores:
\begin{enumerate}
    \item Creación de dos máquinas virtuales que simulan una situación en la que un cliente (una de las máquinas) que solicitará a un servidor (la otra máquina) la revisión de la integridad del sistema de archivos original.
    \item Crear un programa capaz de recorrer el sistema de archivos desde un directorio determinado y generar un archivo “.csv” con la ruta de cada archivo y el Hash asociado a cada archivo
    \item Crear una conexión capaz de transmitir archivos “.csv” entre ambas máquinas y crear los elementos necesarios para la comunicación, en algún momento debe poderse establecer dicha comunicación de forma automática una vez al día
    \item Decidir y tener implementada una estructura de datos adecuada para almacenar en la máquina servidor los datos provenientes del cliente.
    \item Implementar una función de verificación en la máquina servidor capaz de comprobar si alguno de los Hash que llegan del cliente es distinto de los originales que están almacenados
    \item Generar un nuevo archivo “.csv” en el servidor que almacene por cada Hash que le ha enviado el cliente, dicho Hash, un MAC (mediante el Hash del Hash anterior y un token generado aleatoriamente y que ambas máquinas conocen) e información relativa a si el Hash transmitido es correcto
    \item En el cliente se debe implementar de nuevo una función de verificación usando el MAC que obtiene el cliente con sistema de archivos y el MAC que llega del servidor
\end{enumerate}

\section{Desarrollo de cada subproblema}
\subsection{Creación de las máquinas virtuales}Se crean dos máquinas virtuales para realizar la simulación usando la herramienta VirtualBox.
\subsection{Recolectar las rutas de cada archivo}Para tratar este problema escribiendo el programa en Python nos ayudamos de las librerías “hashlib” y “csv”, tras recorrer el sistema de archivos de forma recursiva obtenemos el fichero “.csv” con el formato mostrado en la figura 1.
\begin{center}
    \includegraphics[scale=0.62]{111.PNG}
\end{center}

\subsection{Conexión entre máquinas}
Para empezar abrimos un socket en el cliente y el servidor (IP+puerto), la primera vez el servidor abre un socket y se queda escuchando las peticiones de conexión del cliente, para ello usamos la librería socket de Python.  Una vez establecida la conexión se envía un archivo “.csv” que por cada línea se almacene la ruta y el Hash del archivo. Una vez terminada la transferencia del archivo se cierra la conexión para evitar cualquier tipo de ataque en ese puerto.Tras procesar la información en el servidor, se crea otra conexión pero esta vez es el cliente quien se queda escuchando y el servidor es quien envía datos necesarios para realizar la verificación en el cliente pero el proceso es el mismo que se ha llevado a cabo para la conexión anterior. Mediante las librerías Schedule (pip install schedule) y time de Python se consigue que las conexiones de cliente a servidor y de servidor a cliente se establezcan automáticamente cada día (86400 segundos). Para realizar tests el tiempo se ha reducido a 10 s. Durante algunas pruebas nos hemos percatado de que a veces falla la conexión ya que el servidor tarda unos milisegundos en realizar el procesamiento de los datos y cuando este trata de enviar datos al cliente después ya se ha cerrado la conexión por parte del cliente, por tanto el tiempo que tarda el servidor en realizar la segunda parte de la conexión debe ser de al menos un segundo inferior a la del cliente. Otra solución podría ser dejar siempre abierto el puerto del servidor y dejar que el cliente se autentique en cada conexión pero por falta de tiempo y ya que no es necesario para este proyecto, hemos decidido dejarlo implementado como se ha descrito.
\subsection{Estructura de datos}
Para almacenar la información y tener acceso rápido y eficiente a la misma hemos tenido en cuenta a la sugerencia del enunciado, pero la complejidad en el peor de los casos a la hora de realizar una búsqueda en un árbol binario normal es de O(n), por ello hemos buscado otras estructuras alternativas en forma de árbol. La mejor opción que hemos encontrado es un Van Emde Boas Tree ya que tanto para operaciones de búsqueda como inserción la complejidad es O(log log n), pero comprender el funcionamiento de este árbol e implementarlo costaría más tiempo del que tenemos disponible para realizar el proyecto. La solución por la que nos hemos decidido finalmente ha sido el Red-Black Tree, el cual mediante el almacenamiento de un bit extra de información por cada nodo del árbol que indica su “color” es capaz de rebalancear las ramas cuando se inserta un elemento evitando así el problema que supone el árbol binario simple y pudiendo hacer consultas con una complejidad de O(log n).La forma de reequilibrar el árbol es mediante normas que conciernen a los “colores” de los nodos, las normas son las siguientes:
5oCada nodo es negro o rojo.oTodos los nodos hoja (NIL) son negros.oUn nodo rojo no tiene un hijo rojo.oDado cualquier nodo, todo camino desde ese nodo hasta las hojas tiene el mismo número de nodos negros.Otro problema que nos encontramos a la hora de tener la información guardada en el árbol es que no queremos tener el árbol cargado en RAM todo el tiempo, si hubiese un corte de alimentación en el equipo perderíamos todos los datos y nos sería complicado si no imposible recuperar los datos originales. La solución es serializar el árbol mediante la librería “pickle” de Python.
\begin{center}
    \includegraphics[scale=0.3]{red-black-tree-java.png}
\end{center}

\subsection{Función de verificación}
Una vez hemos obtenido el fichero “.csv” del cliente con todas las rutas y sendos Hash necesitamos tener de algún modo un programa que compare los Hash almacenados en nuestro árbol con los que se nos han enviado. Para ello la solución que hemos planteado ha sido crear una función dentro de la propia implementación del Red-Black Tree, usando como parámetro de entrada una línea del csv se encuentra el nodo que contiene la ruta indicada y en ese mismo momento se compara el Hash enviado por el cliente con el que se encuentra almacenado junto a la ruta en el árbol.Una vez hecha la función nos planteamos la posibilidad de que desde el cliente se añadieran nuevos archivos, por ello implementamos en la función la posibilidad de insertar nuevos archivos con su Hash en caso de no encontrarlo en el árbol.La función debe retornarnos una tupla de valores dos booleanos y una cadena, donde el primer valor indicará en caso de valer “True” que el Hash consultado es correcto y “False” en otro caso, para el segundo valor, “True” nos indica que la consulta actual ha sido añadida al árbol ya que es nuevo desde la consulta anterior, por último se retorna el Hash almacenado en el árbol, esta información nos es útil para el siguiente paso. Esta función ha sido nombrada en el código fuente como “validation\_and\_search”.Figura 2

\subsection{Generación de una respuesta por parte del servidor}
Para responder al cliente, el servidor debe ser capaz de generar un nuevo “.csv” que almacene los MAC, para ello hemos decidido que esta acción debe llevarse a cabo al mismo tiempo que se realiza la lectura del “.csv” y se consulta cada línea con la función de validación que anteriormente hemos descrito.Por cada línea del “.csv” del cliente, se debe realizar la consulta usando la función de validación, de la cual obtenemos los dos valores booleanos de los que hablamos en el apartado anterior, los cuales serán la información extra que vaya incluida en el “.csv” de respuesta más adelante, tras la comprobación de cada línea se realiza un Hash al Hash retornado por la función de validación junto con el token generando así el MAC, con esto tenemos todos los datos necesarios para crear la nueva línea del “.csv” de respuesta cuyo formato es: Hash del archivo enviado por el cliente, MAC, its\_ok, its\_newDonde “its\_ok” \(valor booleano\) indica si los Hashes coinciden a la hora de comprobarlo en el servidor e “its\_new” \(valor booleano\) indica si ha sido añadido nuevo en el árbol.

\subsection{Validación en el cliente} 
Una vez obtenido el MAC que nos proporciona el servidor usamos la misma función de hashing en el cliente con el Hash que ha obtenido el cliente y el mismo token para obtener otro MAC y se realiza la comparación entre ambos, en caso de ser distintos se advierte de la Texto

Descripción generada automáticamente modificación del archivo, en caso de que el servidor nos advirtiera explícitamente que el archivo ha sido modificado pero los MAC coincidiesen también se comunica.

\section{Debilidades típicas}
\subsection{Colisión}
En nuestro HIDS es extremadamente complicado que encontremos una colisión ya que la función de Hash que utilizamos es SHA-256 teniendo 2256 posibles combinaciones.
\subsection{Almacenamiento}
Evitamos almacenar los Hash originales en ningún lugar de la máquina del cliente, de ese modo si el sistema de archivos del mismo se ve comprometido en esa máquina no habrá posibilidad de que desde ese extremo se modifiquen nuestros Hash originales. Tratando de solucionar este problema nos encontramos con que nuestras comunicaciones entre cliente y servidor podrían llegar a ser interceptadas por un atacante, por ello cliente y servidor usaran un token para obtener un MAC, este token jamás viajara por la red ya que es introducida directamente en la máquina cliente y en el servidor a mano.
\subsection{Alarmas tardías}
Este es un problema que no podemos abordar si queremos ceñirnos al enunciado ya que el proceso se lleva a cabo solo una vez al día, podríamos solventarlo aumentando la cantidad de veces que se realiza el proceso, pero podría suponer un estorbo para el funcionamiento normal del cliente. Otra solución podría ser la de implementar el HIDS de forma que cada vez que se requiere algún archivo del cliente se compruebe la integridad del archivo, pero de nuevo podría ralentizar el cliente


\section{Resultados y tests}
\begin{center}
    \includegraphics[width=\textwidth]{servrer_first_run1.PNG}
    \includegraphics[width=\textwidth]{servrer_first_run2.PNG}
    \includegraphics[width=\textwidth]{client_first_run.PNG}
\end{center}

\section{Conclusiones y comentarios}
Debido a que el proyecto está dedicado a la confidencialidad de la información y que no hay suficiente tiempo, no se han implementado otras medidas de seguridad que serían altamente recomendables como la ocultación del token tanto en cliente como en servidor, 
Codificar los logs y el borrado de los archivos auxiliares producidos tras las comunicaciones entre cliente y servidor…Es importante hacer que los scripts de nuestro HIDS deban ser ejecutados, leídos y modificados solo por super usuario para evitar que alguien no propietario de las máquinas manipule el protocolo descrito.

\end{document}
