<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>商品管理</span>
          <div style="display:flex;gap:8px">
            <el-button @click="exportProducts">导出Excel</el-button>
            <el-button type="primary" @click="openAdd">新增商品</el-button>
          </div>
        </div>
      </template>

<!-- 搜索/分类/排序/筛选栏 -->
<div style="margin-bottom:10px;display:flex;flex-direction:column;gap:8px">
  <div style="display:flex;gap:8px;flex-wrap:wrap">
    <el-input v-model="keyword" placeholder="搜索商品名称或条码" clearable @input="loadProducts" style="flex:1;min-width:150px">
      <template #prefix><el-icon><Search /></el-icon></template>
    </el-input>
    <el-select v-model="categoryId" placeholder="选择分类" clearable @change="loadProducts" style="flex:1;min-width:120px">
      <el-option v-for="c in categories" :key="c.id" :value="c.id">
        <div style="display:flex;justify-content:space-between;align-items:center;width:100%">
          <span>{{ c.name }}</span>
          <el-badge :value="c.product_count" :max="999" type="primary" style="margin-left:8px" />
        </div>
      </el-option>
      <template #footer>
        <el-button text style="width:100%;padding:8px 0" @click="categoryDialogVisible = true">✏️ 编辑分类</el-button>
      </template>
    </el-select>
    <el-select v-model="sortBy" placeholder="排序方式" clearable @change="loadProducts" style="flex:1;min-width:120px">
      <el-option label="默认顺序" value="" />
      <el-option label="名称 A→Z" value="name_asc" />
      <el-option label="名称 Z→A" value="name_desc" />
      <el-option label="库存从多到少" value="stock_desc" />
      <el-option label="库存从少到多" value="stock_asc" />
      <el-option label="售价从高到低" value="price_desc" />
      <el-option label="售价从低到高" value="price_asc" />
      <el-option label="最近入库" value="stock_in_desc" />
      <el-option label="最久未入库" value="stock_in_asc" />
    </el-select>
  </div>
  <div style="display:flex;gap:6px;flex-wrap:wrap">
    <el-check-tag :checked="filterSpecial" @change="filterSpecial = !filterSpecial; loadProducts()" style="font-size:12px">有特价</el-check-tag>
    <el-check-tag :checked="filterInStock" @change="filterInStock = !filterInStock; loadProducts()" type="success" style="font-size:12px">有库存</el-check-tag>
    <el-check-tag :checked="filterNoStock" @change="filterNoStock = !filterNoStock; loadProducts()" type="danger" style="font-size:12px">无库存</el-check-tag>
    <el-check-tag :checked="filterLowStock" @change="filterLowStock = !filterLowStock; loadProducts()" type="warning" style="font-size:12px">库存紧张</el-check-tag>
  </div>
</div>

<!-- 全选/结果统计行 -->
<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap">
  <span style="font-size:13px;color:#999">显示 {{ products.length }} / {{ total }} 件</span>
  <el-button size="small" @click="selectAll">全选当前页 ({{ products.length }})</el-button>
  <el-button size="small" @click="selectedIds = []" v-if="selectedIds.length > 0">取消全选</el-button>
  <span v-if="selectedIds.length > 0" style="font-size:13px;color:#409eff;font-weight:bold">已选 {{ selectedIds.length }} 件</span>
</div>

<!-- 批量操作栏 -->
<div v-if="selectedIds.length > 0" style="margin-bottom:12px;display:flex;align-items:center;gap:10px;background:#e8f4fd;padding:10px 14px;border-radius:8px;flex-wrap:wrap">
  <span style="font-size:13px;color:#409eff;font-weight:bold">已选 {{ selectedIds.length }} 件商品</span>
  <el-button size="small" @click="selectedIds = []">取消选择</el-button>
  <el-button size="small" type="primary" @click="openBatchPrice">批量改售价</el-button>
  <el-button size="small" type="danger" @click="openBatchSpecial">批量设特价</el-button>
  <el-button size="small" type="warning" @click="openBatchCategory">批量改分类</el-button>
</div>

<!-- 商品网格 -->
<div v-loading="loading" class="product-grid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px">
  <div
    v-for="p in products" :key="p.id"
    :style="`border:2px solid ${selectedIds.includes(p.id) ? '#409eff' : '#e4e7ed'};border-radius:8px;overflow:hidden;cursor:pointer;transition:box-shadow 0.2s;position:relative;display:flex;flex-direction:column`"
    @mouseenter="e => e.currentTarget.style.boxShadow='0 4px 16px rgba(0,0,0,0.12)'"
    @mouseleave="e => e.currentTarget.style.boxShadow='none'"
  >
    <div style="width:100%;padding-top:75%;background:#f5f7fa;position:relative;flex-shrink:0">
      <div style="position:absolute;top:0;left:0;right:0;bottom:0;display:flex;align-items:center;justify-content:center;overflow:hidden">
        <div style="position:absolute;top:6px;left:6px;z-index:10" @click.stop="toggleSelect(p.id)">
          <el-checkbox :model-value="selectedIds.includes(p.id)" />
        </div>
        <div v-if="p.category_name" style="position:absolute;top:6px;right:6px;z-index:10;background:rgba(64,158,255,0.85);color:#fff;font-size:10px;padding:2px 6px;border-radius:8px;max-width:75px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" :title="p.category_name">
          {{ p.category_name }}
        </div>
        <img v-if="p.image" :src="BASE_URL+p.image" style="width:100%;height:100%;object-fit:cover;cursor:pointer" @click="openDetail(p)" />
        <el-icon v-else style="font-size:48px;color:#c0c4cc;cursor:pointer" @click="openDetail(p)"><Picture /></el-icon>
      </div>
    </div>
    <div style="padding:8px 10px;flex:1;overflow:hidden" @click="openDetail(p)">
      <div style="font-weight:bold;font-size:13px;margin-bottom:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" :title="p.name">{{ p.name }}</div>
      <div v-if="p.name_es" style="font-size:11px;color:#888;margin-bottom:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">🇪🇸 {{ p.name_es }}</div>
      <div style="font-size:12px;color:#666">规格：{{ p.spec || '-' }}</div>
      <div style="font-size:12px;color:#666">货号：{{ p.item_no || p.barcode || '-' }}</div>
      <div :style="`font-size:12px;font-weight:bold;${p.stock <= 0 ? 'color:#f56c6c' : p.stock < 10 ? 'color:#e6a23c' : 'color:#666'}`">
        库存：{{ p.stock }}
        <span v-if="p.stock <= 0" style="font-size:10px">⚠ 无库存</span>
        <span v-else-if="p.stock < 10" style="font-size:10px">⚠ 紧张</span>
      </div>
      <div style="font-size:12px;color:#e6a23c">进价：${{ p.cost_price ?? '-' }}</div>
      <div style="font-size:12px;color:#67c23a">售价：${{ p.sell_price ?? '-' }}</div>
      <div v-if="p.special_price" style="font-size:12px;color:#f56c6c;font-weight:bold">
        特价：${{ p.special_price }}
        <span v-if="p.sell_price" style="font-size:11px;color:#aaa;font-weight:normal">(-{{ calcDiscount(p.sell_price, p.special_price) }}%)</span>
      </div>
      <div v-if="p.last_stock_in" style="font-size:10px;color:#bbb;margin-top:2px">入库：{{ p.last_stock_in.slice(0,10) }}</div>
    </div>
    <div style="padding:0 10px 10px;flex-shrink:0">
      <el-button size="small" type="success" style="width:100%" @click.stop="openStockIn(p)">商品入库</el-button>
    </div>
  </div>
</div>

      <div v-if="products.length === 0 && !loading" style="text-align:center;color:#aaa;padding:40px 0">暂无商品</div>

      <div style="display:flex;justify-content:center;margin-top:20px">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next, jumper"
          background
          @current-change="fetchProducts"
        />
      </div>
    </el-card>

    <!-- 商品详情弹窗 -->
    <el-dialog v-model="detailVisible" title="商品详情" width="750px">
      <div style="display:flex;gap:24px">
        <div style="width:260px;flex-shrink:0">
          <div style="width:260px;height:195px;background:#f5f7fa;border-radius:8px;overflow:hidden;display:flex;align-items:center;justify-content:center;margin-bottom:12px">
            <img v-if="detailProduct.image" :src="BASE_URL+detailProduct.image" style="width:100%;height:100%;object-fit:cover" />
            <el-icon v-else style="font-size:64px;color:#c0c4cc"><Picture /></el-icon>
          </div>
          <el-upload :auto-upload="false" :on-change="handleImageChange" :show-file-list="false" accept="image/*">
            <el-button size="small" style="width:100%">上传图片</el-button>
          </el-upload>
          <el-button size="small" type="success" style="width:100%;margin-top:8px" @click="openStockIn(detailProduct)">商品入库</el-button>
        </div>
        <div style="flex:1">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="商品名称">{{ detailProduct.name }}</el-descriptions-item>
            <el-descriptions-item label="🇪🇸 西语名称">{{ detailProduct.name_es || '-' }}</el-descriptions-item>
            <el-descriptions-item label="条码">{{ detailProduct.barcode || '-' }}</el-descriptions-item>
            <el-descriptions-item label="货号">{{ detailProduct.item_no || '-' }}</el-descriptions-item>
            <el-descriptions-item label="分类">{{ detailProduct.category_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="规格">{{ detailProduct.spec || '-' }}</el-descriptions-item>
            <el-descriptions-item label="每包数量">{{ detailProduct.middle_pack ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="每件数量">{{ detailProduct.piece ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="进价">${{ detailProduct.cost_price ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="售价">${{ detailProduct.sell_price ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="特价">
              <span v-if="detailProduct.special_price" style="color:#f56c6c;font-weight:bold">
                ${{ detailProduct.special_price }}
                <span v-if="detailProduct.sell_price" style="font-size:12px;color:#aaa;font-weight:normal">
                  (-{{ calcDiscount(detailProduct.sell_price, detailProduct.special_price) }}%)
                </span>
              </span>
              <span v-else style="color:#aaa">无</span>
            </el-descriptions-item>
            <el-descriptions-item label="库存">{{ detailProduct.stock }}</el-descriptions-item>
            <el-descriptions-item label="最后入库">{{ detailProduct.last_stock_in || '-' }}</el-descriptions-item>
            <el-descriptions-item label="备注">{{ detailProduct.remark || '-' }}</el-descriptions-item>
          </el-descriptions>
          <div style="margin-top:16px">
            <div style="font-weight:bold;margin-bottom:8px">入库历史</div>
            <el-table :data="stockHistory" size="small" max-height="180">
              <el-table-column prop="created_at" label="入库时间" width="150" />
              <el-table-column prop="quantity" label="数量" width="70" />
              <el-table-column label="类型" width="90">
                <template #default="{ row }">
                  <el-tag v-if="row.source==='manual_new'" type="success" size="small">新增商品</el-tag>
                  <el-tag v-else-if="row.source==='manual_add'" type="primary" size="small">库存增加</el-tag>
                  <el-tag v-else-if="row.source==='import'" type="warning" size="small">导入添加</el-tag>
                  <el-tag v-else size="small">-</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="cost_price" label="进价" width="70" />
            </el-table>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="openEdit(detailProduct)">编辑</el-button>
        <el-button type="danger" @click="deleteProduct(detailProduct.id)">删除</el-button>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑商品' : '新增商品'" width="540px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="条形码"><el-input v-model="form.barcode" /></el-form-item>
        <el-form-item label="货号"><el-input v-model="form.item_no" /></el-form-item>
        <el-form-item label="商品名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="🇪🇸 西语名称">
          <el-input v-model="form.name_es" placeholder="西班牙语名称（选填）" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="选择分类" style="width:100%">
            <el-option v-for="c in categories" :key="c.id" :value="c.id">
              <div style="display:flex;justify-content:space-between;align-items:center;width:100%">
                <span>{{ c.name }}</span>
                <el-badge :value="c.product_count" :max="999" type="primary" style="margin-left:8px" />
              </div>
            </el-option>
            <template #footer>
              <el-button text style="width:100%;padding:8px 0" @click="categoryDialogVisible = true">✏️ 编辑分类</el-button>
            </template>
          </el-select>
        </el-form-item>
        <el-form-item label="规格"><el-input v-model="form.spec" /></el-form-item>
        <el-form-item label="每包数量"><el-input-number v-model="form.middle_pack" :min="1" /></el-form-item>
        <el-form-item label="每件数量"><el-input-number v-model="form.piece" :min="0" /></el-form-item>
        <el-form-item label="进价"><el-input-number v-model="form.cost_price" :precision="2" :min="0" @change="recalcSellPrice" /></el-form-item>
        <el-form-item label="售价">
          <div style="display:flex;gap:8px;align-items:center">
            <el-input-number v-model="form.sell_price" :precision="2" :min="0" style="width:130px" />
            <span style="color:#999;font-size:12px">利润率</span>
            <el-input-number v-model="form._margin" :precision="0" :min="0" :max="999" :step="5" style="width:130px"
              @change="val => { if(form.cost_price) form.sell_price = +(form.cost_price * (1 + (val||0) / 100)).toFixed(2) }" />
            <span style="color:#999;font-size:12px">%</span>
          </div>
        </el-form-item>
        <el-form-item label="特价">
          <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
            <el-input-number v-model="form.special_price" :precision="2" :min="0" style="width:150px" />
            <span v-if="form.special_price && form.sell_price" style="font-size:12px;color:#f56c6c">-{{ calcDiscount(form.sell_price, form.special_price) }}%</span>
            <el-button size="small" type="danger" @click="form.special_price = null" v-if="form.special_price">清除特价</el-button>
            <span style="font-size:12px;color:#aaa">不填则无特价</span>
          </div>
        </el-form-item>
        <el-form-item v-if="!isEdit" label="初始库存"><el-input-number v-model="form.stock" :min="0" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProduct">保存</el-button>
      </template>
    </el-dialog>

    <!-- 商品入库弹窗 -->
    <el-dialog v-model="stockInVisible" title="商品入库" width="400px">
      <el-form :model="stockInForm" label-width="90px">
        <el-form-item label="商品名称"><span>{{ stockInProduct.name }}</span></el-form-item>
        <el-form-item label="当前库存"><span>{{ stockInProduct.stock }}</span></el-form-item>
        <el-form-item label="入库数量"><el-input-number v-model="stockInForm.quantity" :min="1" /></el-form-item>
        <el-form-item label="进价"><el-input-number v-model="stockInForm.cost_price" :precision="2" :min="0" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="stockInForm.remark" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockInVisible = false">取消</el-button>
        <el-button type="primary" @click="submitStockIn">确认入库</el-button>
      </template>
    </el-dialog>

    <!-- 裁剪弹窗 -->
    <el-dialog v-model="cropperVisible" title="裁剪图片" width="620px" :close-on-click-modal="false">
      <div style="height:400px">
        <VueCropper ref="cropperRef" :img="cropperImg" :fixed="true" :fixed-number="[4, 3]" :auto-crop="true" :center-box="true" output-type="jpeg" />
      </div>
      <template #footer>
        <el-button @click="cropperVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCrop">确认裁剪并上传</el-button>
      </template>
    </el-dialog>

    <!-- 批量改售价弹窗 -->
    <el-dialog v-model="batchPriceVisible" title="批量修改售价" width="400px">
      <el-form label-width="90px">
        <el-form-item label="修改方式">
          <el-radio-group v-model="batchPriceMode">
            <el-radio value="fixed">固定金额</el-radio>
            <el-radio value="margin">按利润率</el-radio>
            <el-radio value="adjust">涨/降幅</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="batchPriceMode === 'fixed'" label="售价">
          <el-input-number v-model="batchPriceVal" :precision="2" :min="0" style="width:100%" />
        </el-form-item>
        <el-form-item v-else-if="batchPriceMode === 'margin'" label="利润率">
          <div style="display:flex;align-items:center;gap:8px">
            <el-input-number v-model="batchMarginVal" :precision="0" :min="0" :max="999" style="width:150px" />
            <span>%（售价 = 进价 × (1 + x%)）</span>
          </div>
        </el-form-item>
        <template v-else>
          <el-form-item label="调整方向">
            <el-radio-group v-model="batchAdjustDir">
              <el-radio value="up">涨价</el-radio>
              <el-radio value="down">降价</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="调整幅度">
            <div style="display:flex;align-items:center;gap:8px">
              <el-input-number v-model="batchAdjustVal" :precision="1" :min="0.1" :max="99" style="width:120px" />
              <span>%</span>
            </div>
          </el-form-item>
          <div style="font-size:12px;color:#666;margin-left:90px;background:#f5f7fa;padding:8px 12px;border-radius:6px">
            例：售价 $100 → ${{ batchAdjustDir === 'up' ? (100*(1+batchAdjustVal/100)).toFixed(2) : (100*(1-batchAdjustVal/100)).toFixed(2) }}
          </div>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="batchPriceVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBatchPrice">确认修改 {{ selectedIds.length }} 件</el-button>
      </template>
    </el-dialog>

    <!-- 批量设特价弹窗 -->
    <el-dialog v-model="batchSpecialVisible" title="批量设置特价" width="420px">
      <el-form label-width="90px">
        <el-form-item label="设置方式">
          <el-radio-group v-model="batchSpecialMode">
            <el-radio value="fixed">固定金额</el-radio>
            <el-radio value="percent">按折扣%</el-radio>
            <el-radio value="clear">清除特价</el-radio>
          </el-radio-group>
        </el-form-item>
        <template v-if="batchSpecialMode === 'fixed'">
          <el-form-item label="特价金额">
            <el-input-number v-model="batchSpecialVal" :precision="2" :min="0.01" style="width:160px" />
          </el-form-item>
          <div style="font-size:12px;color:#aaa;margin-left:90px">所有选中商品统一设为此特价</div>
        </template>
        <template v-else-if="batchSpecialMode === 'percent'">
          <el-form-item label="折扣">
            <div style="display:flex;align-items:center;gap:8px">
              <span style="color:#666">售价的</span>
              <el-input-number v-model="batchSpecialPercent" :precision="0" :min="1" :max="99" style="width:100px" />
              <span>%</span>
              <span style="color:#f56c6c;font-size:12px">（优惠 {{ 100-batchSpecialPercent }}%）</span>
            </div>
          </el-form-item>
          <div style="font-size:12px;color:#666;margin-left:90px;background:#f5f7fa;padding:8px 12px;border-radius:6px">
            例：售价 $100 → 特价 ${{ (100 * batchSpecialPercent / 100).toFixed(2) }}（优惠 ${{ (100 - 100 * batchSpecialPercent / 100).toFixed(2) }}）
          </div>
        </template>
        <template v-else>
          <div style="color:#aaa;font-size:13px;padding:8px 0 0 90px">将清除所有选中商品的特价</div>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="batchSpecialVisible = false">取消</el-button>
        <el-button type="danger" @click="submitBatchSpecial">确认设置 {{ selectedIds.length }} 件</el-button>
      </template>
    </el-dialog>

    <!-- 批量改分类弹窗 -->
    <el-dialog v-model="batchCategoryVisible" title="批量修改分类" width="480px">
      <div style="margin-bottom:12px;font-size:13px;color:#666">
        已选 <b style="color:#409eff">{{ selectedIds.length }}</b> 件商品，当前分类分布：
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px">
        <el-tag v-for="(count, name) in selectedCategoryStats" :key="name" type="info" size="small">{{ name }}：{{ count }} 件</el-tag>
      </div>
      <el-form label-width="80px">
        <el-form-item label="目标分类">
          <el-select v-model="batchCategoryVal" placeholder="选择分类" style="width:100%">
            <el-option v-for="c in categories" :key="c.id" :value="c.id">
              <div style="display:flex;justify-content:space-between;align-items:center;width:100%">
                <span>{{ c.name }}</span>
                <el-badge :value="c.product_count" :max="999" type="primary" style="margin-left:8px" />
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchCategoryVisible = false">取消</el-button>
        <el-button type="warning" @click="submitBatchCategory">确认修改 {{ selectedIds.length }} 件</el-button>
      </template>
    </el-dialog>

    <!-- 分类管理弹窗 -->
    <el-dialog v-model="categoryDialogVisible" title="分类管理" width="550px">
      <div style="display:flex;gap:8px;margin-bottom:16px;align-items:flex-start">
        <div style="flex:1;display:flex;flex-direction:column;gap:6px">
          <el-input v-model="newCategoryName" placeholder="中文名称" @keyup.enter="addCategory" />
          <el-input v-model="newCategoryNameEs" placeholder="🇪🇸 西语名称（选填）" @keyup.enter="addCategory" />
        </div>
        <el-button type="primary" @click="addCategory" style="height:72px">添加</el-button>
      </div>
      <el-table :data="categories" stripe>
        <el-table-column label="中文名称">
          <template #default="{ row }">
            <el-input v-if="row._editing" v-model="row._editName" size="small" placeholder="中文" />
            <span v-else>{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="🇪🇸 西语名称">
          <template #default="{ row }">
            <el-input v-if="row._editing" v-model="row._editNameEs" size="small" placeholder="Español" />
            <span v-else style="color:#888">{{ row.name_es || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="商品数" width="70" align="center">
          <template #default="{ row }">
            <el-badge :value="row.product_count" :max="999" type="primary" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <template v-if="row._editing">
              <el-button size="small" type="success" @click="saveEditCategory(row)">保存</el-button>
              <el-button size="small" @click="row._editing = false">取消</el-button>
            </template>
            <template v-else>
              <el-button size="small" @click="row._editing = true; row._editName = row.name; row._editNameEs = row.name_es || ''">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteCategory(row)">删除</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Picture } from '@element-plus/icons-vue'
import request, { BASE_URL } from '../utils/request'
import axios from 'axios'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import 'vue-cropper/dist/index.css'
import { VueCropper } from 'vue-cropper'

const products = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 50
const loading = ref(false)
const categories = ref([])
const keyword = ref('')
const categoryId = ref(null)
const sortBy = ref('')
const filterSpecial = ref(false)
const filterInStock = ref(false)
const filterNoStock = ref(false)
const filterLowStock = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const stockInVisible = ref(false)
const cropperVisible = ref(false)
const categoryDialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const detailProduct = ref({})
const stockHistory = ref([])
const cropperImg = ref('')
const cropperRef = ref(null)
const uploadingProductId = ref(null)
const stockInProduct = ref({})
const stockInForm = ref({ quantity: 1, cost_price: 0, remark: '' })
const newCategoryName = ref('')
const newCategoryNameEs = ref('')
const selectedIds = ref([])
const batchPriceVisible = ref(false)
const batchSpecialVisible = ref(false)
const batchCategoryVisible = ref(false)
const batchPriceMode = ref('adjust')
const batchPriceVal = ref(0)
const batchMarginVal = ref(30)
const batchAdjustDir = ref('up')
const batchAdjustVal = ref(10)
const batchSpecialMode = ref('percent')
const batchSpecialVal = ref(0)
const batchSpecialPercent = ref(90)
const batchCategoryVal = ref(null)

const form = ref({
  barcode: '', item_no: '', name: '', name_es: '', category_id: null,
  spec: '', middle_pack: 1, piece: null,
  cost_price: 0, sell_price: 0, special_price: null, stock: 0, remark: '', _margin: null
})

const calcDiscount = (sellPrice, specialPrice) => {
  if (!sellPrice || !specialPrice) return 0
  return ((1 - specialPrice / sellPrice) * 100).toFixed(0)
}

const selectedCategoryStats = computed(() => {
  const selected = products.value.filter(p => selectedIds.value.includes(p.id))
  const stats = {}
  selected.forEach(p => {
    const name = p.category_name || '未分类'
    stats[name] = (stats[name] || 0) + 1
  })
  return stats
})

const selectAll = () => { selectedIds.value = products.value.map(p => p.id) }

const recalcSellPrice = (val) => {
  if (form.value._margin && val) {
    form.value.sell_price = +(val * (1 + form.value._margin / 100)).toFixed(2)
  }
}

const toggleSelect = (id) => {
  const idx = selectedIds.value.indexOf(id)
  if (idx === -1) selectedIds.value.push(id)
  else selectedIds.value.splice(idx, 1)
}

const openBatchPrice = () => { batchPriceMode.value = 'adjust'; batchAdjustDir.value = 'up'; batchAdjustVal.value = 10; batchPriceVal.value = 0; batchMarginVal.value = 30; batchPriceVisible.value = true }
const openBatchSpecial = () => { batchSpecialMode.value = 'percent'; batchSpecialPercent.value = 90; batchSpecialVal.value = 0; batchSpecialVisible.value = true }
const openBatchCategory = () => { batchCategoryVal.value = null; batchCategoryVisible.value = true }

const buildProductParams = () => {
  const params = {}
  if (keyword.value) params.keyword = keyword.value
  if (categoryId.value) params.category_id = categoryId.value
  if (sortBy.value) params.sort_by = sortBy.value
  if (filterSpecial.value) params.filter_special = true
  if (filterInStock.value) params.filter_in_stock = true
  if (filterNoStock.value) params.filter_no_stock = true
  if (filterLowStock.value) params.filter_low_stock = true
  return params
}

const loadProducts = async () => {
  currentPage.value = 1
  await fetchProducts()
}

const fetchProducts = async () => {
  loading.value = true
  try {
    const res = await request.get('/products/', {
      params: { ...buildProductParams(), page: currentPage.value, page_size: pageSize }
    })
    products.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => { categories.value = await request.get('/categories/') }

const exportProducts = async () => {
  const res = await request.get('/products/', {
    params: { ...buildProductParams(), page: 1, page_size: 99999 }
  })
  const data = res.items.map(p => ({
    '商品名称': p.name, '西语名称': p.name_es || '', '条码': p.barcode || '',
    '货号': p.item_no || '', '分类': p.category_name || '', '规格': p.spec || '',
    '每包数量': p.middle_pack ?? '', '每件数量': p.piece ?? '',
    '进价': p.cost_price ?? '', '售价': p.sell_price ?? '',
    '特价': p.special_price ?? '',
    '折扣': p.special_price && p.sell_price ? `-${calcDiscount(p.sell_price, p.special_price)}%` : '',
    '库存': p.stock, '最后入库': p.last_stock_in || '', '备注': p.remark || ''
  }))
  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '商品列表')
  const buf = XLSX.write(wb, { type: 'array', bookType: 'xlsx' })
  saveAs(new Blob([buf], { type: 'application/octet-stream' }), `商品列表_${new Date().toLocaleDateString()}.xlsx`)
}

const submitBatchPrice = async () => {
  const selected = products.value.filter(p => selectedIds.value.includes(p.id))
  let updated = 0
  for (const p of selected) {
    let newPrice = null
    if (batchPriceMode.value === 'fixed') newPrice = batchPriceVal.value
    else if (batchPriceMode.value === 'margin') newPrice = p.cost_price ? +(p.cost_price * (1 + batchMarginVal.value / 100)).toFixed(2) : null
    else if (batchPriceMode.value === 'adjust' && p.sell_price) {
      const factor = batchAdjustDir.value === 'up' ? (1 + batchAdjustVal.value / 100) : (1 - batchAdjustVal.value / 100)
      newPrice = +(p.sell_price * factor).toFixed(2)
    }
    if (newPrice !== null && newPrice > 0) { await request.put(`/products/${p.id}`, { sell_price: newPrice }); updated++ }
  }
  ElMessage.success(`已更新 ${updated} 件商品售价`)
  batchPriceVisible.value = false; selectedIds.value = []; loadProducts()
}

const submitBatchSpecial = async () => {
  const selected = products.value.filter(p => selectedIds.value.includes(p.id))
  let updated = 0
  for (const p of selected) {
    let specialVal = null
    if (batchSpecialMode.value === 'fixed') specialVal = batchSpecialVal.value > 0 ? batchSpecialVal.value : null
    else if (batchSpecialMode.value === 'percent') specialVal = p.sell_price ? +(p.sell_price * batchSpecialPercent.value / 100).toFixed(2) : null
    await request.put(`/products/${p.id}`, { special_price: specialVal }); updated++
  }
  ElMessage.success(`已更新 ${updated} 件商品特价`)
  batchSpecialVisible.value = false; selectedIds.value = []; loadProducts()
}

const submitBatchCategory = async () => {
  if (!batchCategoryVal.value) { ElMessage.warning('请选择分类'); return }
  for (const id of selectedIds.value) await request.put(`/products/${id}`, { category_id: batchCategoryVal.value })
  ElMessage.success(`已更新 ${selectedIds.value.length} 件商品分类`)
  batchCategoryVisible.value = false; selectedIds.value = []; loadProducts()
}

const addCategory = async () => {
  if (!newCategoryName.value.trim()) { ElMessage.warning('请输入分类名称'); return }
  await request.post('/categories/', { name: newCategoryName.value.trim(), name_es: newCategoryNameEs.value.trim() || null })
  ElMessage.success('添加成功'); newCategoryName.value = ''; newCategoryNameEs.value = ''; loadCategories()
}

const saveEditCategory = async (row) => {
  if (!row._editName.trim()) { ElMessage.warning('分类名称不能为空'); return }
  await request.put(`/categories/${row.id}`, { name: row._editName.trim(), name_es: row._editNameEs?.trim() || null })
  ElMessage.success('更新成功'); row._editing = false; loadCategories()
}

const deleteCategory = async (row) => {
  if (row.product_count > 0) { ElMessage.warning(`该分类下有 ${row.product_count} 个商品，无法删除`); return }
  try {
    await ElMessageBox.confirm(`确定删除分类"${row.name}"？`, '提示', { type: 'warning' })
  } catch { return }
  await request.delete(`/categories/${row.id}`); ElMessage.success('删除成功'); loadCategories()
}

const openDetail = async (p) => {
  detailProduct.value = { ...p }; cropperImg.value = ''; detailVisible.value = true
  stockHistory.value = await request.get(`/products/${p.id}/stock-history`)
}

const handleImageChange = (file) => {
  uploadingProductId.value = detailProduct.value.id
  const reader = new FileReader()
  reader.onload = (e) => { cropperImg.value = e.target.result; cropperVisible.value = true }
  reader.readAsDataURL(file.raw)
}

const submitCrop = () => {
  cropperRef.value.getCropBlob(async (blob) => {
    const formData = new FormData()
    formData.append('file', blob, 'image.jpg')
    const token = localStorage.getItem('token')
    const res = await axios.post(`${BASE_URL}/api/products/${uploadingProductId.value}/image`, formData, { headers: { Authorization: `Bearer ${token}` } })
    detailProduct.value.image = res.data.image; ElMessage.success('图片上传成功'); cropperVisible.value = false; loadProducts()
  })
}

const openStockIn = (p) => {
  stockInProduct.value = p; stockInForm.value = { quantity: 1, cost_price: p.cost_price || 0, remark: '' }; stockInVisible.value = true
}

const submitStockIn = async () => {
  if (!stockInForm.value.quantity || stockInForm.value.quantity < 1) { ElMessage.warning('请输入入库数量'); return }
  const res = await request.post(`/products/${stockInProduct.value.id}/stockin`, stockInForm.value)
  ElMessage.success(`入库成功，当前库存：${res.new_stock}`); stockInVisible.value = false; detailVisible.value = false; loadProducts()
}

const openAdd = () => {
  isEdit.value = false
  form.value = { barcode: '', item_no: '', name: '', name_es: '', category_id: null, spec: '', middle_pack: 1, piece: null, cost_price: 0, sell_price: 0, special_price: null, stock: 0, remark: '', _margin: null }
  dialogVisible.value = true
}

const openEdit = (row) => {
  isEdit.value = true; editId.value = row.id; form.value = { ...row, _margin: null }; detailVisible.value = false; dialogVisible.value = true
}

const saveProduct = async () => {
  if (!form.value.name) { ElMessage.warning('请输入商品名称'); return }
  const payload = { ...form.value }; delete payload._margin
  if (isEdit.value) await request.put(`/products/${editId.value}`, payload)
  else await request.post('/products/', payload)
  ElMessage.success('保存成功'); dialogVisible.value = false; loadProducts()
}

const deleteProduct = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除该商品？', '提示', { type: 'warning' })
  } catch { return }
  await request.delete(`/products/${id}`); ElMessage.success('删除成功'); detailVisible.value = false; loadProducts()
}

onMounted(() => { loadProducts(); loadCategories() })
</script>