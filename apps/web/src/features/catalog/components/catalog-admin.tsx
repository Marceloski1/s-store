import { brandService } from "@/services/admin-services/brand"
import { categoryService } from "@/services/admin-services/category"
import { NamedResourceManager } from "@/features/catalog/components/named-resource-manager"

export function CatalogAdmin() {
  return (
    <div className="grid items-start gap-6 lg:grid-cols-2">
      <NamedResourceManager title="Marcas" gateway={brandService} />
      <NamedResourceManager title="Categorías" gateway={categoryService} />
    </div>
  )
}
