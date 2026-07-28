import React from "react";
import { Input, Button, Select } from "antd";
import { SearchOutlined, UploadOutlined } from "@ant-design/icons";

const { Search } = Input;

interface SearchBarProps {
  placeholder?: string;
  onSearch: (query: string) => void;
  onUploadCSV?: () => void;
  className?: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = "Search by address or transaction hash...",
  onSearch,
  onUploadCSV,
  className,
}) => {
  return (
    <div className={className} style={{ display: "flex", gap: 12 }}>
      <Search
        placeholder={placeholder}
        allowClear
        enterButton={<SearchOutlined />}
        size="large"
        onSearch={onSearch}
        style={{ flex: 1 }}
      />
      {onUploadCSV && (
        <Button
          icon={<UploadOutlined />}
          size="large"
          onClick={onUploadCSV}
        >
          Upload CSV
        </Button>
      )}
    </div>
  );
};

interface FilterOption {
  label: string;
  value: string;
}

interface FilterDropdownProps {
  label: string;
  options: FilterOption[];
  selected?: string;
  onSelect: (value: string) => void;
  className?: string;
}

export const FilterDropdown: React.FC<FilterDropdownProps> = ({
  label,
  options,
  selected,
  onSelect,
  className,
}) => {
  return (
    <div className={className}>
      <div style={{ marginBottom: 4, fontSize: 14, fontWeight: 500 }}>
        {label}
      </div>
      <Select
        value={selected || undefined}
        placeholder="All"
        onChange={onSelect}
        style={{ width: "100%" }}
        options={[
          { label: "All", value: "" },
          ...options,
        ]}
      />
    </div>
  );
};
