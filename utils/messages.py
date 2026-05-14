"""Mensajes del Bot"""
from config import CHANNEL_URL, VERIFY_COST, HELP_NOTION_URL


def get_welcome_message(full_name: str, invited_by: bool = False) -> str:
    """Mensaje de bienvenida"""
    msg = (
        f"🎉 ¡Bienvenido, {full_name}!\n"
        "Te has registrado correctamente y has recibido 1 punto.\n"
    )
    if invited_by:
        msg += "Gracias por unirte mediante invitación. ¡Tu invitador ha recibido 2 puntos!\n"

    msg += (
        "\nEste bot puede completar automáticamente verificaciones de SheerID.\n"
        "Guía rápida:\n"
        "/about - Conoce las funciones del bot\n"
        "/balance - Ver tus puntos disponibles\n"
        "/help - Ver la lista completa de comandos\n\n"
        "Consigue más puntos:\n"
        "/qd - Check-in diario (+1 punto)\n"
        "/invite - Invitar a amigos (+2 puntos por persona)\n"
        f"Únete a nuestro canal: {CHANNEL_URL}"
    )
    return msg


def get_about_message() -> str:
    """Información sobre el bot"""
    return (
        "🤖 Bot de Autoverificación SheerID\n"
        "\n"
        "Funciones principales:\n"
        "- Completa automáticamente verificaciones SheerID para estudiantes/profesores.\n"
        "- Soporta: Gemini One Pro, ChatGPT Teacher K12, Spotify Student, YouTube Student y Bolt.new Teacher.\n"
        "\n"
        "Cómo obtener puntos:\n"
        "- Regalo de bienvenida: 1 punto\n"
        "- Check-in diario: +1 punto\n"
        "- Invitar amigos: +2 puntos por persona\n"
        "- Usar códigos de canje (según reglas del código)\n"
        f"- Únete al canal: {CHANNEL_URL}\n"
        "\n"
        "Modo de uso:\n"
        "1. Inicia la verificación en la web oficial y copia el enlace completo de SheerID.\n"
        "2. Envía /verify, /verify2, /verify3, /verify4 o /verify5 seguido del enlace.\n"
        "3. Espera a que el bot procese la solicitud y mira el resultado.\n"
        "4. En Bolt.new, el bot obtiene el código automáticamente. Para consulta manual usa: /getV4Code <id_de_verificación>\n"
        "\n"
        "Usa /help para más comandos."
    )


def get_help_message(is_admin: bool = False) -> str:
    """Mensaje de ayuda"""
    msg = (
        "📖 Ayuda - Bot de Verificación SheerID\n"
        "\n"
        "Comandos de usuario:\n"
        "/start - Registrarse en el bot\n"
        "/about - Funciones del bot\n"
        "/balance - Ver tus puntos\n"
        "/qd - Check-in diario (+1 punto)\n"
        "/invite - Generar enlace de invitación (+2 puntos)\n"
        "/use <código> - Canjear puntos con código\n"
        f"/verify <link> - Gemini One Pro (-{VERIFY_COST} puntos)\n"
        f"/verify2 <link> - ChatGPT Teacher K12 (-{VERIFY_COST} puntos)\n"
        f"/verify3 <link> - Spotify Student (-{VERIFY_COST} puntos)\n"
        f"/verify4 <link> - Bolt.new Teacher (-{VERIFY_COST} puntos)\n"
        f"/verify5 <link> - YouTube Student (-{VERIFY_COST} puntos)\n"
        "/getV4Code <id> - Obtener código de Bolt.new\n"
        "/help - Ver este mensaje de ayuda\n"
        f"¿Fallo en la verificación?: {HELP_NOTION_URL}\n"
    )

    if is_admin:
        msg += (
            "\nComandos de Administrador:\n"
            "/addbalance <ID> <puntos> - Añadir puntos a un usuario\n"
            "/block <ID> - Banear usuario\n"
            "/white <ID> - Desbanear usuario\n"
            "/blacklist - Ver lista negra\n"
            "/genkey <código> <puntos> [usos] [días] - Generar código de canje\n"
            "/listkeys - Ver lista de códigos\n"
            "/broadcast <texto> - Enviar mensaje a todos los usuarios\n"
        )

    return msg


def get_insufficient_balance_message(current_balance: int) -> str:
    """Mensaje de saldo insuficiente"""
    return (
        f"❌ ¡Puntos insuficientes! Necesitas {VERIFY_COST} puntos y tienes {current_balance}.\n\n"
        "Consigue más puntos:\n"
        "- Check-in diario: /qd\n"
        "- Invitar amigos: /invite\n"
        "- Canjear código: /use <código>"
    )


def get_verify_usage_message(command: str, service_name: str) -> str:
    """Instrucciones de uso de comandos de verificación"""
    return (
        f"Uso: {command} <enlace_SheerID>\n\n"
        "Ejemplo:\n"
        f"{command} https://services.sheerid.com/verify/xxx/?verificationId=xxx\n\n"
        "Cómo obtener el enlace:\n"
        f"1. Visita la página de {service_name}\n"
        "2. Inicia el proceso de verificación\n"
        "3. Copia la URL completa de la barra de direcciones\n"
        "4. Envíala usando el comando {command}"
    )
