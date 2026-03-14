<template>
  <div>
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
      <el-button @click="$router.push('/stats')" :icon="ArrowLeft">返回</el-button>
      <h2 style="margin:0">商品统计</h2>
    </div>

    <el-card style="margin-bottom:20px">
      <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
        <span style="font-weight:bold;font-size:15px">统计时间段</span>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width:280px"
          @change="loadAll"
        />
        <el-button @click="setToday">今天</el-button>
        <el-button @click="setThisWeek">本周</el-button>
        <el-button @click="setThisMonth">本月</el-button>
      </div>
    </el-card>

    <el-card>
      <template #header><span>商品出入库盈亏</span></template>
      <div v-if="productStats.length === 0" style="text-align:center;color:#999;padding:40px">
        该时间段内无商品出入库记录
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px">
        <div
          v-for="p in productStats" :key="p.id"
          style="border:1px solid #e4e7ed;border-radius:8px;overflow:hidden"
        >
          <div style="width:100%;padding-top:75%;position:relative;background:#f5f7fa">
            <div style="position:absolute;top:0;left:0;right:0;bottom:0;display:flex;align-items:center;justify-content:center;overflow:hidden">
              <img v-if="p.image" :src="BASE_URL+p.image" style="width:100%;height:100%;object-fit:cover" />
              <el-icon v-else style="font-size:48px;color:#c0c4cc"><Picture /></el-icon>
            </div>
          </div>
          <div style="padding:10px">
            <div style="font-weight:bold;font-size:13px;margin-bottom:6px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" :title="p.name">{{ p.name }}</div>
            <div style="font-size:12px;color:#666;margin-bottom:2px">规格：{{ p.spec || '-' }}</div>
            <div style="font-size:12px;color:#666;margin-bottom:2px">当前库存：{{ p.stock }}</div>
            <el-divider style="margin:6px 0" />
            <div style="font-size:12px;color:#f56c6c">入库：{{ p.total_in_qty }}件 / ${{ p.total_in_cost }}</div>
            <div style="font-size:12px;color:#67c23a">销售：{{ p.total_out_qty }}件 / ${{ p.total_out_sales }}</div>
            <div :style="p.profit >= 0 ? 'font-size:12px;font-weight:bold;color:#409eff' : 'font-size:12px;font-weight:bold;color:#f56c6c'">
              {{ p.profit >= 0 ? '盈利' : '亏损' }}：${{ Math.abs(p.profit) }}
            </div>
            <el-divider style="margin:6px 0" />
            <div style="font-size:11px;color:#aaa">最后入库：{{ p.last_in || '-' }}</div>
            <div style="font-size:11px;color:#aaa">最后销售：{{ p.last_out || '-' }}</div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ArrowLeft, Picture } from '@element-plus/icons-vue'
import request, { BASE_URL } from '../utils/request'

const dateRange = ref(null)
const productStats = ref([])

const getParams = () => {
  if (dateRange.value && dateRange.value[0]) {
    return { start: dateRange.value[0], end: dateRange.value[1] }
  }
  const today = new Date().toISOString().slice(0, 10)
  return { start: today, end: today }
}

const loadAll = async () => {
  const params = getParams()
  productStats.value = await request.get('/stats/products', { params })
}

const setToday = () => {
  const today = new Date().toISOString().slice(0, 10)
  dateRange.value = [today, today]
  loadAll()
}

const setThisWeek = () => {
  const now = new Date()
  const day = now.getDay() || 7
  const mon = new Date(now)
  mon.setDate(now.getDate() - day + 1)
  dateRange.value = [mon.toISOString().slice(0, 10), now.toISOString().slice(0, 10)]
  loadAll()
}

const setThisMonth = () => {
  const now = new Date()
  const first = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().slice(0, 10)
  dateRange.value = [first, now.toISOString().slice(0, 10)]
  loadAll()
}

onMounted(() => {
  setToday()
})
</script>