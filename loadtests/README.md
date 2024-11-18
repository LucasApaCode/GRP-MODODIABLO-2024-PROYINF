# Pruebas de carga con Apache JMeter

En el hito 5 nos solicitaron diseñar un plan de pruebas de carga haciendo uso de la herramienta Apache JMeter, en donde debiamos limitar este diseño a un conjunto de mínimo tres pruebas y a la ejecución de una de esas pruebas. Como grupo, tomamos en consideración la historia de usuario relacionada al "Acceso seguro y privado" para diseñar el plan de performance, el cual consiste en cuatro pruebas en las que experimentamos con el login de nuestra misma aplicación web. Todo esto se realizó considerando que es importante y relevante testear el flujo de autenticación, dado que queremos corroborar que la herramienta que estamos construyendo brinda seguridad y eficiencia en condiciones de carga elevada. 

Ahora, este plan lo realizamos con el objetivo de evaluar el mismo rendimiento y la capacidad de respuesta que tiene el login/logout de nuestra página bajo variadas condiciones de carga. Esto lo realizamos implementando las solicitudes HTTP correspondientes que se pudieron identificar al momento de que un usuario registrado ingresa a su cuenta privada. Lo anterior también se hace para corroborar y asegurar que el acceso a esta herramienta es rápido y fiable para los usuarios médicos que podrían utilizar esta plataforma, teniendo como meta que el tiempo de respuesta menor al segundo.  

A continuación se van a describir el conjunto de pruebas realizado: 
1. Prueba de carga baja:
   * Usuarios: 50
   * Periodo Ramp_up: 30 segundos
2. Prueba de carga media:
   * Usuarios: 500
   * Periodo Ramp_up: 120 segundos
3. Prueba de carga alta:
   * Usuarios: 1000
   * Periodo Ramp_up: 180 segundos
4. Prueba de carga extrema:
   * Usuarios: 1000
   * Periodo Ramp_up: 30 segundos

Analizando las fotografías, se puede ver que en las primeras tres pruebas se logra cumplir con el objetivo relacionado al tiempo de respuesta para cada una de las solicitudes HTTP. Esto es de esperarse debido a que en estas primeras pruebas, al aumentar la cantidad de usuarios, también incrementamos el tiempo, lo cual obviamente ayuda a manejar la misma carga de usuarios. Pero observando la cuarta y última prueba, se puede decir que no cumple con la meta mencionada anteriormente, ya que una de las solicitudes necesarias para el logín tiene un tiempo mayor a 1000 milisegundos. Esto se debe a que sobrecargamos de forma deliberada al sistema con una gran cantidad de usuarios. Esto también generó otro tipo de fallos, como errores en el mismo servidor al no poder manejar la carga (lo cual se observó en JMeter cuando aparecieron errores HTTP). 
