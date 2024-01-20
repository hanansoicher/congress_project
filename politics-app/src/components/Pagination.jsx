// eslint-disable-next-line no-unused-vars
import React from 'react';
import PropTypes from 'prop-types';

const Pagination = ({ nPages, currentPage, setCurrentPage }) => {

    Pagination.propTypes = {
        nPages: PropTypes.number.isRequired,
        currentPage: PropTypes.number.isRequired,
        setCurrentPage: PropTypes.func.isRequired,
    };

    const handlePageChange = (page) => {
        const totalPages = nPages;
        if (page >= 1 && page <= totalPages) {
            setCurrentPage(page);
        }
    };

    return (
        <div className="pagination">
            <button
                disabled={currentPage === 1}
                onClick={() => handlePageChange(currentPage - 1)}
            >
                Previous
            </button>
            <span>{currentPage}</span>
            <button
                disabled={currentPage === nPages}
                onClick={() => handlePageChange(currentPage + 1)}
            >
                Next
            </button>
        </div>
    );
};

export default Pagination;
