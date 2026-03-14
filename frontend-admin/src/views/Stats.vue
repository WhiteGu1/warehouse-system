<template>
  <div>
    <h2 style="margin-bottom:20px">统计分析</h2>
    <el-row :gutter="20" style="row-gap:16px">
      <el-col :xs="24" :sm="8">
        <el-card
          shadow="hover"
          style="cursor:pointer;text-align:center;padding:20px 0"
          @click="$router.push('/stats/flow')"
        >
          <el-icon style="font-size:48px;color:#409eff;margin-bottom:12px"><Money /></el-icon>
          <div style="font-size:18px;font-weight:bold;margin-bottom:8px">流水统计</div>
          <div style="color:#999;font-size:13px">查看入库支出与销售收入的流水明细，分析整体盈亏情况</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card
          shadow="hover"
          style="cursor:pointer;text-align:center;padding:20px 0"
          @click="$router.push('/stats/products')"
        >
          <el-icon style="font-size:48px;color:#67c23a;margin-bottom:12px"><Goods /></el-icon>
          <div style="font-size:18px;font-weight:bold;margin-bottom:8px">商品统计</div>
          <div style="color:#999;font-size:13px">查看每件商品的入库成本、销售营收与盈亏情况</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { Money, Goods } from '@element-plus/icons-vue'
</script>