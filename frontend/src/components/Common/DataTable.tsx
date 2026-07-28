import React from "react";
import { Table, Empty, Pagination as AntPagination } from "antd";
import type { ColumnsType, TableProps } from "antd/es/table";

interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  className?: string;
  width?: number | string;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  onRowClick?: (item: T) => void;
  className?: string;
  emptyMessage?: string;
  loading?: boolean;
  pagination?: false | {
    current?: number;
    pageSize?: number;
    total?: number;
    onChange?: (page: number, pageSize: number) => void;
  };
}

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  onRowClick,
  className,
  emptyMessage = "No data found",
  loading = false,
  pagination,
}: DataTableProps<T>) {
  // Convert custom columns to Ant Design columns
  const antColumns: ColumnsType<T> = columns.map((col) => ({
    key: col.key,
    dataIndex: col.key,
    title: col.header,
    width: col.width,
    className: col.className,
    render: col.render
      ? (_: any, record: T) => col.render!(record)
      : undefined,
  }));

  const tableProps: TableProps<T> = {
    columns: antColumns,
    dataSource: data,
    loading,
    className,
    rowKey: (record, index) => record.id || record.key || index,
    onRow: onRowClick
      ? (record) => ({
          onClick: () => onRowClick(record),
          style: { cursor: "pointer" },
        })
      : undefined,
    locale: {
      emptyText: <Empty description={emptyMessage} />,
    },
    pagination: pagination === false ? false : {
      current: pagination?.current || 1,
      pageSize: pagination?.pageSize || 10,
      total: pagination?.total || data.length,
      onChange: pagination?.onChange,
      showSizeChanger: true,
      showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`,
    },
  };

  return <Table {...tableProps} />;
}

// Legacy Pagination component (for backward compatibility)
interface PaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalItems,
  pageSize,
  onPageChange,
  className,
}) => {
  return (
    <div className={className} style={{ display: "flex", justifyContent: "flex-end", padding: "16px 0" }}>
      <AntPagination
        current={currentPage}
        total={totalItems}
        pageSize={pageSize}
        onChange={onPageChange}
        showSizeChanger
        showTotal={(total, range) => `${range[0]}-${range[1]} of ${total} items`}
      />
    </div>
  );
};
