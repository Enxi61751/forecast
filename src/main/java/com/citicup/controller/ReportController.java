package com.citicup.controller;

import com.citicup.common.ApiResponse;
import com.citicup.service.ReportService;
import com.citicup.entity.RiskReport;
import com.lowagie.text.*;
import com.lowagie.text.pdf.BaseFont;
import com.lowagie.text.pdf.PdfWriter;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.io.ByteArrayOutputStream;

@RestController
@RequestMapping("/api/report")
@RequiredArgsConstructor
public class ReportController {

    private final ReportService reportService;

    @PostMapping("/generate/{predictionRunId}")
    public ApiResponse<Long> generate(@PathVariable Long predictionRunId) {
        return ApiResponse.ok(reportService.generateReport(predictionRunId));
    }
    @GetMapping("/download")
    public ResponseEntity<byte[]> downloadReport() {

        try {

            // 查询最新的报告
            RiskReport report = reportService.getLatestReport();

            // 创建 PDF 输出流
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();

            Document document = new Document(PageSize.A4, 50, 50, 60, 60);
            PdfWriter.getInstance(document, outputStream);

            document.open();

            // 中文字体
            BaseFont baseFont = BaseFont.createFont(
                    "STSong-Light",
                    "UniGB-UCS2-H",
                    BaseFont.NOT_EMBEDDED
            );

            Font titleFont = new Font(baseFont, 20, Font.BOLD);
            Font subtitleFont = new Font(baseFont, 12);
            Font bodyFont = new Font(baseFont, 12);

            // 标题
            Paragraph title = new Paragraph("原油价格风险分析报告", titleFont);
            title.setAlignment(Element.ALIGN_CENTER);
            title.setSpacingAfter(20);
            document.add(title);

            // 报告信息
            Paragraph info = new Paragraph(
                    "预测批次ID：" + report.getPredictionRunId()
                            + "    生成时间：" + report.getCreatedAt(),
                    subtitleFont
            );
            info.setAlignment(Element.ALIGN_CENTER);
            info.setSpacingAfter(30);
            document.add(info);

            //  正文标题
            Paragraph sectionTitle = new Paragraph("一、风险分析摘要", bodyFont);
            sectionTitle.setSpacingAfter(10);
            document.add(sectionTitle);

            //  正文内容（自动换行）
            Paragraph content = new Paragraph(report.getReportText(), bodyFont);
            content.setFirstLineIndent(24); // 首行缩进
            content.setLeading(20);         // 行间距
            document.add(content);

            document.close();

            byte[] pdfBytes = outputStream.toByteArray();

            return ResponseEntity.ok()
                    .header(HttpHeaders.CONTENT_DISPOSITION,
                            "attachment; filename=risk_report.pdf")
                    .contentType(MediaType.APPLICATION_PDF)
                    .body(pdfBytes);

        } catch (Exception e) {
            throw new RuntimeException("生成PDF失败", e);
        }
    }
}
