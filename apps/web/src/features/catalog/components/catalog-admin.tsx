import { brandsGateway } from "@/features/catalog/api/brands"
import { categoriesGateway } from "@/features/catalog/api/categories"
import { NamedResourceManager } from "@/features/catalog/components/named-resource-manager"

export function CatalogAdmin() {
  return (
    <div className="grid items-start gap-6 lg:grid-cols-2">
      <NamedResourceManager title="Marcas" gateway={brandsGateway} />
      <NamedResourceManager title="Categorías" gateway={categoriesGateway} />
    </div>
  )
}
