<?php
// filepath: /var/www/html/test.php

// サンプルページのタイトルとメッセージ
$title = "サンプルPHPページ";
$message = "PHPで動的なウェブページを作成しました！";

?>
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $title; ?></title>
</head>
<body>
    <h1><?php echo $title; ?></h1>
    <p><?php echo $message; ?></p>
    <p>現在の日時: <?php echo date("Y年m月d日 H:i:s"); ?></p>
</body>
</html>