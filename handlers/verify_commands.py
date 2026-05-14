"""Procesador de comandos de verificación"""
import asyncio
import logging
import httpx
import time
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import VERIFY_COST
from database_mysql import Database
from one.sheerid_verifier import SheerIDVerifier as OneVerifier
from k12.sheerid_verifier import SheerIDVerifier as K12Verifier
from spotify.sheerid_verifier import SheerIDVerifier as SpotifyVerifier
from youtube.sheerid_verifier import SheerIDVerifier as YouTubeVerifier
from Boltnew.sheerid_verifier import SheerIDVerifier as BoltnewVerifier
from utils.messages import get_insufficient_balance_message, get_verify_usage_message

# Intento de importar control de concurrencia
try:
    from utils.concurrency import get_verification_semaphore
except ImportError:
    def get_verification_semaphore(verification_type: str):
        return asyncio.Semaphore(3)

logger = logging.getLogger(__name__)


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Maneja /verify - Gemini One Pro"""
    user_id = update.effective_user.id [cite: 81]

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Has sido bloqueado y no puedes usar esta función.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Por favor, usa /start para registrarte primero.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify", "Gemini One Pro")
        )
        return

    url = context.args[0] [cite: 82]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = OneVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Enlace de SheerID inválido. Por favor, revísalo.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Error al descontar puntos. Inténtalo de nuevo.")
        return [cite: 83]

    processing_msg = await update.message.reply_text(
        f"Iniciando verificación Gemini One Pro...\n"
        f"ID de Verificación: {verification_id}\n"
        f"Se han descontado {VERIFY_COST} puntos.\n\n"
        "Espera, por favor. Esto tardará 1-2 minutos..."
    )

    try:
        verifier = OneVerifier(verification_id)
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification( [cite: 84]
            user_id,
            "gemini_one_pro",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ ¡Verificación exitosa!\n\n"
            if result.get("pending"): [cite: 85]
                result_msg += "Documento enviado, esperando revisión manual.\n"
            if result.get("redirect_url"):
                result_msg += f"Enlace de redirección:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text( [cite: 86]
                f"❌ Verificación fallida: {result.get('message', 'Error desconocido')}\n\n"
                f"Se han devuelto {VERIFY_COST} puntos."
            )
    except Exception as e:
        logger.error("Error en el proceso: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Ocurrió un error en el proceso: {str(e)}\n\n"
            f"Se han devuelto {VERIFY_COST} puntos." [cite: 87]
        )


async def verify2_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Maneja /verify2 - ChatGPT Teacher K12"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Has sido bloqueado y no puedes usar esta función.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Por favor, usa /start para registrarte primero.")
        return

    if not context.args:
        await update.message.reply_text( [cite: 88]
            get_verify_usage_message("/verify2", "ChatGPT Teacher K12")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = K12Verifier.parse_verification_id(url)
    if not verification_id: [cite: 89]
        await update.message.reply_text("Enlace de SheerID inválido. Por favor, revísalo.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Error al descontar puntos. Inténtalo de nuevo.")
        return

    processing_msg = await update.message.reply_text(
        f"Iniciando verificación ChatGPT Teacher K12...\n"
        f"ID de Verificación: {verification_id}\n"
        f"Se han descontado {VERIFY_COST} puntos.\n\n"
        "Espera, por favor. Esto tardará 1-2 minutos..."
    )

    try: [cite: 90]
        verifier = K12Verifier(verification_id)
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "chatgpt_teacher_k12",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

    if result["success"]: [cite: 91]
            result_msg = "✅ ¡Verificación exitosa!\n\n"
            if result.get("pending"):
                result_msg += "Documento enviado, esperando revisión manual.\n"
            if result.get("redirect_url"):
                result_msg += f"Enlace de redirección:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
    else: [cite: 92]
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verificación fallida: {result.get('message', 'Error desconocido')}\n\n"
                f"Se han devuelto {VERIFY_COST} puntos."
            )
    except Exception as e:
        logger.error("Error en el proceso: %s", e) [cite: 93]
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Ocurrió un error en el proceso: {str(e)}\n\n"
            f"Se han devuelto {VERIFY_COST} puntos."
        )


async def verify3_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Maneja /verify3 - Spotify Student"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Has sido bloqueado y no puedes usar esta función.")
        return

    if not db.user_exists(user_id): [cite: 94]
        await update.message.reply_text("Por favor, usa /start para registrarte primero.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify3", "Spotify Student")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text( [cite: 95]
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = SpotifyVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Enlace de SheerID inválido. Por favor, revísalo.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Error al descontar puntos. Inténtalo de nuevo.")
        return

    processing_msg = await update.message.reply_text( [cite: 96]
        f"🎵 Iniciando verificación Spotify Student...\n"
        f"Se han descontado {VERIFY_COST} puntos.\n\n"
        "📝 Generando información de estudiante...\n"
        "🎨 Creando carné estudiantil PNG...\n"
        "📤 Subiendo documentos..."
    )

    semaphore = get_verification_semaphore("spotify_student")

    try:
        async with semaphore:
            verifier = SpotifyVerifier(verification_id)
            result = await asyncio.to_thread(verifier.verify) [cite: 97]
            
        db.add_verification(
            user_id,
            "spotify_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        ) [cite: 98]

        if result["success"]:
            result_msg = "✅ ¡Verificación de Spotify exitosa!\n\n"
            if result.get("pending"):
                result_msg += "✨ Documentos enviados, esperando revisión de SheerID\n"
                result_msg += "⏱️ Tiempo estimado: pocos minutos\n\n"
            if result.get("redirect_url"): [cite: 99]
                result_msg += f"🔗 Enlace de redirección:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verificación fallida: {result.get('message', 'Error desconocido')}\n\n"
                f"Se han devuelto {VERIFY_COST} puntos." [cite: 100]
            )
    except Exception as e:
        logger.error("Error en verificación Spotify: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Ocurrió un error en el proceso: {str(e)}\n\n"
            f"Se han devuelto {VERIFY_COST} puntos."
        )


async def verify4_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Maneja /verify4 - Bolt.new Teacher"""
    user_id = update.effective_user.id [cite: 101]

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Has sido bloqueado y no puedes usar esta función.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Por favor, usa /start para registrarte primero.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify4", "Bolt.new Teacher")
        )
        return

    url = context.args[0] [cite: 102]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    external_user_id = BoltnewVerifier.parse_external_user_id(url)
    verification_id = BoltnewVerifier.parse_verification_id(url)

    if not external_user_id and not verification_id:
        await update.message.reply_text("Enlace de SheerID inválido. Por favor, revísalo.")
        return [cite: 103]

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Error al descontar puntos. Inténtalo de nuevo.")
        return

    processing_msg = await update.message.reply_text(
        f"🚀 Iniciando verificación Bolt.new Teacher...\n"
        f"Se han descontado {VERIFY_COST} puntos.\n\n"
        "📤 Subiendo documentos..."
    )

    semaphore = get_verification_semaphore("bolt_teacher")

    try:
        async with semaphore: [cite: 104]
            verifier = BoltnewVerifier(url, verification_id=verification_id)
            result = await asyncio.to_thread(verifier.verify)

        if not result.get("success"):
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text( [cite: 105]
                f"❌ Error al subir documentos: {result.get('message', 'Error desconocido')}\n\n"
                f"Se han devuelto {VERIFY_COST} puntos."
            )
            return
        
        vid = result.get("verification_id", "")
        if not vid:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text( [cite: 106]
                f"❌ No se pudo obtener el ID de verificación.\n\n"
                f"Se han devuelto {VERIFY_COST} puntos."
            )
            return
        
        await processing_msg.edit_text(
            f"✅ ¡Documentos enviados!\n" [cite: 107]
            f"📋 ID: `{vid}`\n\n"
            f"🔍 Obteniendo código automáticamente...\n"
            f"(Espera máximo 20 segundos)"
        )
        
        code = await _auto_get_reward_code(vid, max_wait=20, interval=5)
        
        if code: [cite: 108]
            result_msg = (
                f"🎉 ¡Verificación exitosa!\n\n"
                f"✅ Documentos enviados\n"
                f"✅ Revisión aprobada\n"
                f"✅ Código obtenido\n\n" [cite: 109]
                f"🎁 Tu Código: `{code}`\n"
            )
            if result.get("redirect_url"):
                result_msg += f"\n🔗 Enlace:\n{result['redirect_url']}"
            
            await processing_msg.edit_text(result_msg)
            
            db.add_verification( [cite: 110]
                user_id,
                "bolt_teacher",
                url,
                "success",
                f"Code: {code}", [cite: 111]
                vid
            )
        else:
            await processing_msg.edit_text(
                f"✅ ¡Documentos enviados correctamente!\n\n"
                f"⏳ El código aún no se ha generado (puede tardar 1-5 min)\n\n" [cite: 112]
                f"📋 ID de verificación: `{vid}`\n\n"
                f"💡 Usa este comando para consultar más tarde:\n"
                f"`/getV4Code {vid}`\n\n"
                f"Nota: Los puntos ya se han consumido."
            )
            
            db.add_verification( [cite: 113]
                user_id,
                "bolt_teacher",
                url,
                "pending",
                "Waiting for review", [cite: 114]
                vid
            )
            
    except Exception as e:
        logger.error("Error en Bolt.new: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Ocurrió un error: {str(e)}\n\n"
            f"Se han devuelto {VERIFY_COST} puntos."
        )


async def _auto_get_reward_code( [cite: 115]
    verification_id: str,
    max_wait: int = 20,
    interval: int = 5
) -> Optional[str]:
    import time
    start_time = time.time()
    attempts = 0 [cite: 116]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            elapsed = int(time.time() - start_time)
            attempts += 1
            
            if elapsed >= max_wait: [cite: 117]
                logger.info(f"Tiempo agotado ({elapsed}s), consultar manualmente")
                return None
            
            try:
                response = await client.get( [cite: 118]
                    f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    current_step = data.get("currentStep") [cite: 119]
                    
                    if current_step == "success":
                        code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
                        if code: [cite: 120]
                            logger.info(f"✅ Código obtenido: {code}")
                            return code
                    elif current_step == "error": [cite: 121]
                        logger.warning(f"Revisión fallida: {data.get('errorIds', [])}")
                        return None [cite: 122]
                
                await asyncio.sleep(interval)
                
            except Exception as e: [cite: 123]
                logger.warning(f"Error consultando código: {e}")
                await asyncio.sleep(interval)
    
    return None


async def verify5_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Maneja /verify5 - YouTube Student Premium"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Has sido bloqueado y no puedes usar esta función.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Por favor, usa /start para registrarte primero.")
        return

    if not context.args: [cite: 124]
        await update.message.reply_text(
            get_verify_usage_message("/verify5", "YouTube Student Premium")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = YouTubeVerifier.parse_verification_id(url) [cite: 125]
    if not verification_id:
        await update.message.reply_text("Enlace de SheerID inválido. Por favor, revísalo.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Error al descontar puntos. Inténtalo de nuevo.")
        return

    processing_msg = await update.message.reply_text(
        f"📺 Iniciando verificación YouTube Student...\n"
        f"Se han descontado {VERIFY_COST} puntos.\n\n"
        "📝 Generando información de estudiante...\n" [cite: 126]
        "🎨 Creando carné estudiantil PNG...\n"
        "📤 Subiendo documentos..."
    )

    semaphore = get_verification_semaphore("youtube_student")

    try:
        async with semaphore:
            verifier = YouTubeVerifier(verification_id)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification( [cite: 127]
            user_id,
            "youtube_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ ¡Verificación de YouTube exitosa!\n\n"
            if result.get("pending"): [cite: 128]
                result_msg += "✨ Documentos enviados, esperando revisión de SheerID\n"
                result_msg += "⏱️ Tiempo estimado: pocos minutos\n\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 Enlace de redirección:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else: [cite: 129]
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verificación fallida: {result.get('message', 'Error desconocido')}\n\n"
                f"Se han devuelto {VERIFY_COST} puntos."
            )
    except Exception as e:
        logger.error("Error en YouTube: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text( [cite: 130]
            f"❌ Ocurrió un error en el proceso: {str(e)}\n\n"
            f"Se han devuelto {VERIFY_COST} puntos."
        )


async def getV4Code_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Maneja /getV4Code - Bolt.new Teacher"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Has sido bloqueado y no puedes usar esta función.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Por favor, usa /start para registrarte primero.") [cite: 131]
        return

    if not context.args:
        await update.message.reply_text(
            "Uso: /getV4Code <id_verificacion>\n\n"
            "Ejemplo: /getV4Code 6929436b50d7dc18638890d0\n\n"
            "Obtendrás el id al usar /verify4."
        )
        return

    verification_id = context.args[0].strip()

    processing_msg = await update.message.reply_text( [cite: 132]
        "🔍 Consultando código, espera un momento..."
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
            )

            if response.status_code != 200: [cite: 133]
                await processing_msg.edit_text(
                    f"❌ Error al consultar, código: {response.status_code}\n\n"
                    "Inténtalo más tarde o contacta con soporte."
                )
                return

            data = response.json() [cite: 134]
            current_step = data.get("currentStep")
            reward_code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
            redirect_url = data.get("redirectUrl")

            if current_step == "success" and reward_code:
                result_msg = "✅ ¡Verificación exitosa!\n\n"
                result_msg += f"🎉 Tu Código: `{reward_code}`\n\n" [cite: 135]
                if redirect_url:
                    result_msg += f"Enlace:\n{redirect_url}"
                await processing_msg.edit_text(result_msg)
            elif current_step == "pending":
                await processing_msg.edit_text( [cite: 136]
                    "⏳ Sigue en revisión, por favor espera.\n\n"
                    "Suele tardar entre 1 y 5 minutos."
                )
            elif current_step == "error":
                error_ids = data.get("errorIds", [])
                await processing_msg.edit_text( [cite: 137]
                    f"❌ Verificación fallida\n\n"
                    f"Mensaje: {', '.join(error_ids) if error_ids else 'Error desconocido'}"
                )
            else:
                await processing_msg.edit_text( [cite: 138]
                    f"⚠️ Estado actual: {current_step}\n\n"
                    "El código aún no se ha generado."
                )

    except Exception as e:
        logger.error("Error obteniendo código: %s", e)
        await processing_msg.edit_text(
            f"❌ Error durante la consulta: {str(e)}\n\n" [cite: 139]
            "Inténtalo de nuevo más tarde."
        )
