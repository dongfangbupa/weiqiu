<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
    <title>{% block title %}{% endblock %}</title>
    <link rel="stylesheet" type="text/css" href="./static/css/bootstrap.min.css">
    <%block name="header">${next.header()}</%block>
</head>
<body>
    <nav>
        <div class="left">
            <img src="./image/getheadimg.png">
            <span>C-Level</span>
            <span>酋长网</span>
        </div>
        <div class="right">
            <a href="javascirpt:void(0)">首页</a>
            <a href="javascirpt:void(0)">退出</a>
            <a href="javascirpt:void(0)">信息</a>
            <a href="javascirpt:void(0)">团队</a>
            <a href="javascirpt:void(0)">主页</a>
            <img src="./image/getheadimg.png"/>
        </div>
        
    </nav>
    <%block name="body">${next.body()}</%block>
</body>
<footer>
    <div>
        C-Level
        <ul>
            <li>About Us</li>
            <li>Join Us</li>
            <li>Flowing Us</li>
            <li>Contact Us</li>
            
        </ul>
    </div>
    <div>
        Commercialization
        <ul>
            <li>Advertiser</li>
            <li>Partnership</li>
            <li>Investment</li>
        </ul>
    </div>
    <div>
        Policy
        <ul>
            <li>User Agreement</li>
            <li>Privacy Policy</li>
        </ul>
    </div>
</footer>
<script type="text/javascript" src="./static/js/jquery-1.11.2.min.js"></script>
<script type="text/javascript" src="./static/js/bootstrap.min.js"></script>
<%block name="scripts">${next.scripts()}</%block>
</html>