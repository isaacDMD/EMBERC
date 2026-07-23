export function useChantAudioUpload() {
  const { request } = useApi()

  async function uploaderAudio(fichier: File): Promise<string> {
    const { upload_url, key, fields } = await request<{
      upload_url: string
      key: string
      fields: Record<string, string>
    }>('/chants/upload-url', {
      method: 'POST',
      body: { nom_fichier: fichier.name, content_type: fichier.type },
    })

    const formData = new FormData()
    Object.entries(fields).forEach(([champ, valeur]) => formData.append(champ, valeur))
    formData.append('file', fichier)

    const uploadResponse = await fetch(upload_url, {
      method: 'POST',
      body: formData,
    })
    if (!uploadResponse.ok) {
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