## Quality Issue 1:
**Descripción:** La función identificada tiene una complejidad cognitiva de 52, lo que excede el límite permitido de 15. La complejidad cognitiva es una métrica que mide qué tan difícil es entender y mantener el código, basado en el número de decisiones lógicas (condicionales, bucles, etc.) y el flujo general del programa. Una complejidad tan alta indica que la función es difícil de leer, probar y mantener, lo que aumenta el riesgo de errores y dificulta futuras modificaciones.

**Severidad:** Este problema tiene un gran impacto en la capacidad de mantenimiento de nuestro software.

**Evidencia:**  
![Screenshot del problema](QI1.png)


## Quality Issue 2:
**Descripción:** El código actual permite realizar redirecciones HTTP basadas en datos proporcionados por el usuario, lo que puede exponer el sistema a ataques de redirección abierta (open redirect attacks). Este tipo de vulnerabilidad puede ser explotado para redirigir a los usuarios hacia sitios maliciosos, facilitando ataques como phishing o robo de credenciales.

**Severidad:** Este problema tiene un gran impacto en la seguridad de nuestro software.

**Evidencia:**  
![Screenshot del problema](QI2.png)
