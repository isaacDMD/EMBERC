export function useChantAudioUpload() {
  const { request } = useApi()

  async function uploaderAudio(fichier: File): Promise<string> {
    const { upload_url, key } = await request<{ upload_url: string; key: string }>(
      '/chants/upload-url',
      {
        method: 'POST',
        body: { nom_fichier: fichier.name, content_type: fichier.type },
      }
    )

    const putResponse = await fetch(upload_url, {
      method: 'PUT',
      body: fichier,
      headers: { 'Content-Type': fichier.type },
    })
    if (!putResponse.ok) {
      throw new Error("L'envoi du fichier audio a échoué")
    }

    const { fichier_audio_url } = await request<{ fichier_audio_url: string; taille_octets: number }>(
      '/chants/confirm-upload',
      { method: 'POST', body: { key } }
    )

    return fichier_audio_url
  }

  return { uploaderAudio }
}