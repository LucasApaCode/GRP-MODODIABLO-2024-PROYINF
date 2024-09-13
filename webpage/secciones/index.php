<?php include('../templates/header.php'); ?>

<?php
$url = 'http://localhost:5000/api/endpoint';
$data = array('key' => 'value');

// Iniciar cURL
$ch = curl_init($url);

// Configurar cURL
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));

// Ejecutar cURL y obtener la respuesta
$response = curl_exec($ch);
curl_close($ch);

// Mostrar la respuesta
echo $response;
?>

<?php include('../templates/footer.php'); ?>
