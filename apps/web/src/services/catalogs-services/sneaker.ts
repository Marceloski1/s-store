import { apiClient } from "@/lib/api/client"
import { unwrap, unwrapOrNull } from "@/lib/api/result"
import type { operations } from "@/lib/api/schema"

type CatalogListQuery = NonNullable<
  operations["list_published_sneakers_catalog_sneakers_get"]["parameters"]["query"]
>

export const sneakerService = {
  async list(query: CatalogListQuery) {
    return unwrap(
      await apiClient.GET("/catalog/sneakers", { params: { query } })
    )
  },
  async getBySlug(slug: string) {
    return unwrapOrNull(
      await apiClient.GET("/catalog/sneakers/{slug}", {
        params: { path: { slug } },
      })
    )
  },
}
