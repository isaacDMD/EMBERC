type CategorieMedia = 'audio' | 'video' | 'image' | 'document'

export function useMediaUpload() {
  const { request } = useApi()

  async function uploaderFichier(fichier: File, categorie: CategorieMedia, paroisseId: number): Promise<string> {
    const { upload_url, key } = await request<{ upload_url: string; key: string }>(
      '/medias/upload-url',
      {
        method: 'POST',
        body: {
          nom_fichier: fichier.name,
          content_type: fichier.type,
          type_media: categorie,
          paroisse_id: paroisseId,
        },
      }
    )

    const putResponse = await fetch(upload_url, {
      method: 'PUT',
      body: fichier,
      headers: { 'Content-Type': fichier.type },
    })
    if (!putResponse.ok) {
      throw new Error("L'envoi du fichier a échoué")
    }

    const { url_media } = await request<{ url_media: string; taille_octets: number }>(
      '/medias/confirm-upload',
      { method: 'POST', body: { key, type_media: categorie } }
    )

    return url_media
  }

  return { uploaderFichier }
}