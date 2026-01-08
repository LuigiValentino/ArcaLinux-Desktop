<div align="center">
    <img src="resources/app_icon.png" alt="ArcaLinux Desktop Logo" width="220">
    <h1>ArcaLinux</h1>
    <p>
        Aplicación de escritorio para la generación de documentos comerciales<br>
        <strong>Tickets · Facturas · Códigos QR</strong>
    </p>
</div>

<hr>

<p>
    <strong>ArcaLinux </strong> es una aplicación de escritorio desarrollada en Python,
    diseñada para la creación local de documentos comerciales como tickets, facturas
    y códigos QR de ARCA.
</p>

<p>
    Está orientada a ser <strong>automatizable</strong> y a usuarios no convencionales
    como programadores, contadores y otros rubros técnicos o administrativos.
</p>

<p>
    El objetivo principal del proyecto es ofrecer una herramienta
    <em>offline-first</em>, simple y eficiente, pensada para entornos
    comerciales, administrativos o de uso interno, sin depender de servicios web
    ni conexiones externas.
</p>

<p>
    <strong><u>Disclaimer:</u></strong>
    El programa <strong>no</strong> realiza verificaciones con el servicio web oficial del ARCA.
    Para validación fiscal o integración online se recomienda utilizar productos
    que cumplan con dicha función.
</p>

<hr>

<h2>Características principales</h2>
<ul>
    <li>Aplicación de escritorio para Linux</li>
    <li>Generación de tickets y facturas</li>
    <li>Soporte para códigos QR</li>
    <li>Ejecución local (sin backend ni navegador)</li>
    <li>Arquitectura simple y extensible para automatización</li>
    <li>Exportación de documentos en HTML con QR integrado o separado</li>
</ul>

<hr>

<h2>Automatización e integraciones</h2>

<p>
    ArcaLinux fue diseñado con un enfoque <strong>automation-friendly</strong>.
    Puede integrarse fácilmente en flujos de trabajo existentes,
    tanto de forma manual como automatizada.
</p>

<h3>Casos de uso comunes</h3>
<ul>
    <li>Conversión automática de documentos HTML a PDF</li>
    <li>Impresión directa desde el sistema operativo</li>
    <li>Envío automático de facturas y tickets por correo electrónico</li>
    <li>Generación masiva de documentos mediante scripts</li>
</ul>

<h3>Herramientas recomendadas</h3>

<table>
    <thead>
        <tr>
            <th>Herramienta</th>
            <th>Uso recomendado</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Python</td>
            <td>Integración directa y personalización del flujo de generación</td>
        </tr>
        <tr>
            <td>Selenium (headless)</td>
            <td>Automatización de renderizado, testing o exportación</td>
        </tr>
        <tr>
            <td>Bash + cron</td>
            <td>Ejecución programada de procesos batch</td>
        </tr>
        <tr>
            <td>systemd services / timers</td>
            <td>Ejecución como servicio o tarea programada del sistema</td>
        </tr>
        <tr>
            <td>Makefile</td>
            <td>Workflow reproducible (build, run, deploy)</td>
        </tr>
        <tr>
            <td>wkhtmltopdf / weasyprint</td>
            <td>Conversión confiable de HTML a PDF</td>
        </tr>
        <tr>
            <td>CUPS</td>
            <td>Impresión automatizada en entornos Linux</td>
        </tr>
    </tbody>
</table>

<hr>

<h2>Roadmap y objetivos</h2>
<ul>
    <li>Empaquetado como binario ejecutable (.AppImage / PyInstaller)</li>
    <li>Distribución oficial para Linux</li>
    <li>Compatibilidad con Ubuntu, Arch Linux, Linux Mint y Fedora</li>
    <li>Publicación en Snap Store</li>
</ul>

<hr>

<p>
    Este proyecto puede utilizarse libremente para uso personal o interno.
    No se permite la redistribución modificada bajo la marca
    <strong>Arcynox</strong> o el nombre del autor
    <strong>Luigi Adducci</strong> sin autorización previa.
</p>

